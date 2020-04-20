import os
import random
import time
from collections import deque

import numpy as np
import torch
import torch.nn.functional as F
from torch.nn import Module, Linear, MSELoss
from torch.optim import Adam
from torch.utils.tensorboard import SummaryWriter

from env import Teeko
from tools import moveToPreds, predsToMove


class Net(Module):
    def __init__(self):
        super(Net, self).__init__()
        self.linear1 = Linear(25 * 2, 1_024)
        self.linear1.weight.data.normal_(0, 0.1)

        self.linear2 = Linear(1_024, 1_024)
        self.linear2.weight.data.normal_(0, 0.1)

        self.linear3 = Linear(1_024, 2 + 25 + 8)
        self.linear3.weight.data.normal_(0, 0.1)

    def forward(self, x):
        x = x.view(-1, 25 * 2)
        x = F.leaky_relu(self.linear1(x))
        x = F.leaky_relu(self.linear2(x))
        x = self.linear3(x)
        return x


class DQNAgent(object):
    def __init__(self):
        self.net = Net()
        self.net.load_state_dict(torch.load('net.pth'))

    def getParamsCount(self):
        pp = 0
        for p in list(self.net.parameters()):
            nn = 1
            for s in list(p.size()):
                nn *= s
            pp += nn
        return pp

    def predict(self, state):
        with torch.no_grad():
            state = torch.from_numpy(state).unsqueeze(0).float()
            return self.net(state)[0].numpy()


if __name__ == '__main__':
    # if torch.cuda.is_available():
    #     device = torch.device("cuda:0")
    #     print("Running on the GPU")
    # else:
    device = torch.device("cpu")
    print("Running on the CPU")

    env = Teeko()

    TARGET_INTERVAL = 8_192

    MIN_HISTORY = 4_096
    MAX_HISTORY = 16_384
    history = deque(maxlen=MAX_HISTORY)

    LOSS_HISTORY = 512
    losses = deque(maxlen=LOSS_HISTORY)

    VALID_MOVE_HISTORY = 4_096
    valid_moves = deque(maxlen=VALID_MOVE_HISTORY)

    REWARD_HISTORY = 2_048
    rewards = deque(maxlen=REWARD_HISTORY)

    WIN_HISTORY = 16
    wins = deque(maxlen=WIN_HISTORY)

    epsilon = .05
    EPSILON_DECAY = .99995
    MIN_EPSILON = .05

    BATCH_SIZE = 32
    LR = 1E-5
    DISCOUNT = .9

    WIN_REWARD = 100.
    LOSE_REWARD = -1.
    STEP_REWARD = 0.

    policy_net = Net().to(device)
    pp = 0
    for p in list(policy_net.parameters()):
        nn = 1
        for s in list(p.size()):
            nn *= s
        pp += nn
    print(f'Number of parameters: {pp}')

    LOAD_NET = False
    PREV_NET = ''
    SAVE_INTERVAL = 16_384

    if not os.path.exists('nets/'):
        os.mkdir('nets')
    if LOAD_NET:
        print('Loading prev net')
        policy_net.load_state_dict(torch.load(os.path.join('net', PREV_NET)))

    target_net = Net().to(device)
    target_net.load_state_dict(policy_net.state_dict())

    criterion = MSELoss()
    optimizer = Adam(policy_net.parameters(), lr=LR)
    writer = SummaryWriter(f'logs/{time.time()}')

    step = 0
    while True:
        env.reset()

        last_states = [None, None]
        last_preds = [None, None]
        game_history = []

        adversarial = np.random.choice([1, 2])

        start_step = step
        done = False
        while not done:
            for player_idt in [1, 2]:
                step += 1
                state = env.getState(player_idt != 1)

                if last_states[player_idt - 1] is not None:
                    if player_idt != adversarial:
                        rewards.append(STEP_REWARD)
                    game_history.append((last_states[player_idt - 1], last_preds[player_idt - 1], STEP_REWARD,
                                         state.tolist(), done))

                if (LOAD_NET or len(history) >= MIN_HISTORY) and np.random.random() > epsilon:
                    with torch.no_grad():
                        T = torch.from_numpy(state).unsqueeze(0).float().to(device)
                        preds = (policy_net(T) if player_idt != adversarial else target_net(T))[0].cpu().numpy()
                        move = predsToMove(preds)

                        valid_move = env.moveIsCorrect(move, player_idt)
                        valid_moves.append(valid_move)
                        if not valid_move:
                            move = env.getRandomMove(player_idt)
                            preds = moveToPreds(move)

                else:
                    move = env.getRandomMove(player_idt)
                    preds = moveToPreds(move)

                state, preds = state.tolist(), preds.tolist()
                done = env.step(move, player_idt)

                if done:
                    if player_idt != adversarial:
                        rewards.append(WIN_REWARD)
                    game_history.append((state, preds, WIN_REWARD, state, done))

                    if player_idt == adversarial:
                        rewards.append(LOSE_REWARD)
                    game_history.append((last_states[abs(player_idt - 2)], last_preds[abs(player_idt - 2)],
                                         LOSE_REWARD, state, done))

                last_states[player_idt - 1] = state
                last_preds[player_idt - 1] = preds

                if len(history) >= MIN_HISTORY:
                    if epsilon > MIN_EPSILON:
                        epsilon = max(MIN_EPSILON, epsilon * EPSILON_DECAY)

                    minibatch = random.sample(history, BATCH_SIZE)

                    with torch.no_grad():
                        T_current_states = torch.tensor([transition[0] for transition in minibatch],
                                                        dtype=torch.float, device=device)
                        T_current_qs_list = policy_net(T_current_states)

                        T_new_states = torch.tensor([transition[3] for transition in minibatch],
                                                    dtype=torch.float, device=device)
                        T_future_qs_list = target_net(T_new_states)

                    X = torch.empty((BATCH_SIZE, 25, 2), dtype=torch.float, device=device)
                    y = torch.empty((BATCH_SIZE, 2 + 25 + 8), dtype=torch.float, device=device)

                    for index, (T_current_state, T_pred, T_reward, T_new_state, T_done) in enumerate(minibatch):
                        T_current_qs = T_current_qs_list[index]
                        T_future_qs = T_future_qs_list[index]

                        indexes = [(0, 2), (2, 25), (27, 8)]

                        for start, length in indexes:
                            if not T_done:
                                T_max_future_q = torch.max(T_future_qs[start: start + length])
                                new_q = T_reward + DISCOUNT * T_max_future_q
                            else:
                                new_q = T_reward

                            T_current_qs[start + np.argmax(T_pred[start: start + length])] = new_q

                        X[index] = torch.tensor(T_current_state, dtype=torch.float, device=device)
                        y[index] = T_current_qs

                    optimizer.zero_grad()

                    outputs = policy_net(X)
                    loss = criterion(outputs, y)
                    loss.backward()
                    optimizer.step()

                    losses.append(loss.item())
                    writer.add_scalar('dqn/training_loss', losses[-1], step)

                    if step % TARGET_INTERVAL == TARGET_INTERVAL - 1:
                        target_net.load_state_dict(policy_net.state_dict())

                    if step % SAVE_INTERVAL == SAVE_INTERVAL - 1:
                        torch.save(policy_net.state_dict(),
                                   f'nets/net_{int(time.time())}_{sum(rewards) / len(rewards):.5f}.pth')

                if done:
                    wins.append(player_idt != adversarial)
                    history.extend(game_history)
                    break

                elif step - start_step >= 128:
                    done = True
                    break

        stats_training_loss = sum(losses) / len(losses) if len(losses) != 0 else 0
        stats_rewards = sum(rewards) / len(rewards) if len(rewards) != 0 else 0
        stats_wins = (sum(wins) / len(wins)) * 100 if len(wins) != 0 else 0
        stats_valid_moves = (sum(valid_moves) / len(valid_moves)) * 100 if len(valid_moves) != 0 else 0
        print(f'Training loss: {stats_training_loss:.5f} | '
              f'Epsilon: {epsilon:.5f} | '
              f'Rewards: {stats_rewards:.5f} | '
              f'Wins: {stats_wins:.1f}% | '
              f'Valid moves: {stats_valid_moves:.1f}% | '
              f'Memory size: {len(history)} ({MIN_HISTORY}-{MAX_HISTORY}) | '
              f'Steps: {step}')

        if len(history) >= MIN_HISTORY:
            writer.add_scalar('dqn/rewards', stats_rewards, step)
            writer.add_scalar('dqn/wins', stats_wins, step)
            writer.add_scalar('dqn/valid_moves', stats_valid_moves, step)
