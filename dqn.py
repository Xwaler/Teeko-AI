import torch
import torch.nn.functional as F
from torch.nn import Module, Conv2d, Linear, MSELoss


class Net(Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = Conv2d(3, 64, kernel_size=5, padding=2)
        self.conv2 = Conv2d(64, 64, kernel_size=3)
        self.linear1 = Linear(64 * 3 * 3, 512)
        self.out = Linear(512, 25 + (25 * 8))

    def forward(self, x):
        x = F.leaky_relu(self.conv1(x))
        x = F.leaky_relu(self.conv2(x))
        x = x.view(-1, 64 * 3 * 3)
        x = F.leaky_relu(self.linear1(x))
        x = self.out(x)
        return x


class DQNAgent(object):
    def __init__(self):
        self.net = Net()
        self.net.load_state_dict(torch.load('net_0131071_0.00002804.pth'))

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
    import os
    import random
    import time
    from collections import deque
    import numpy as np

    from torch.utils.tensorboard import SummaryWriter
    from torch.optim import Adam

    from env import Teeko
    from tools import moveToPreds

    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        print("Running on the GPU")
    else:
        device = torch.device("cpu")
        print("Running on the CPU")

    env = Teeko()

    TARGET_INTERVAL = 32_768

    MIN_HISTORY = 65_536
    MAX_HISTORY = 131_072
    history = deque(maxlen=MAX_HISTORY)

    LOSS_HISTORY = 512
    losses = deque(maxlen=LOSS_HISTORY)

    REWARD_HISTORY = 512
    rewards = deque(maxlen=REWARD_HISTORY)

    WIN_HISTORY = 16
    wins = deque(maxlen=WIN_HISTORY)

    epsilon = .80
    EPSILON_DECAY = .99995
    MIN_EPSILON = .02

    BATCH_SIZE = 64
    LR = 1e-5
    DISCOUNT = .9

    WIN_REWARD = 1.
    LOSE_REWARD = -1.
    STEP_REWARD = 0

    policy_net = Net().to(device)
    pp = 0
    for p in list(policy_net.parameters()):
        nn = 1
        for s in list(p.size()):
            nn *= s
        pp += nn
    print(f'Number of parameters: {pp}')

    LOAD_NET = True
    PREV_NET = 'net_0131071_0.00002804.pth'
    SAVE_INTERVAL = 8_192

    if not os.path.exists('nets/'):
        os.mkdir('nets')
    if LOAD_NET:
        print('Loading prev net')
        policy_net.load_state_dict(torch.load(os.path.join('nets', PREV_NET)))

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
        while not done and step - start_step < 256:
            for player_idt in [1, 2]:
                step += 1
                state = env.getState(reverse=player_idt == 2)

                if last_states[player_idt - 1] is not None:
                    if player_idt != adversarial:
                        rewards.append(STEP_REWARD)
                    game_history.append((last_states[player_idt - 1], last_preds[player_idt - 1],
                                         STEP_REWARD, state.tolist(), done))

                if (LOAD_NET or len(history) >= MIN_HISTORY) and np.random.random() > epsilon:
                    with torch.no_grad():
                        T = torch.from_numpy(state).unsqueeze(0).float().to(device)
                        preds = (policy_net(T) if player_idt != adversarial else target_net(T))[0].cpu().numpy()
                        preds, move = env.correctMove(preds, player_idt)

                else:
                    move = env.getRandomMove(player_idt)
                    preds = moveToPreds(move)

                state, preds = state.tolist(), preds.tolist()
                done = env.step(move, player_idt)

                if done:
                    rewards.append(WIN_REWARD if player_idt != adversarial else LOSE_REWARD)
                    wins.append(player_idt != adversarial)

                    game_history.append((state, preds, WIN_REWARD, state, done))
                    game_history.append((last_states[abs(player_idt - 2)], last_preds[abs(player_idt - 2)],
                                         LOSE_REWARD, state, done))

                    history.extend(game_history)

                else:
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

                    X = torch.empty((BATCH_SIZE, 3, 5, 5), dtype=torch.float, device=device)
                    y = torch.empty((BATCH_SIZE, 25 + (25 * 8)), dtype=torch.float, device=device)

                    for index, (T_current_state, T_pred, T_reward, T_new_state, T_done) in enumerate(minibatch):
                        T_current_qs = T_current_qs_list[index]
                        T_future_qs = T_future_qs_list[index]

                        if not T_done:
                            T_max_future_q = torch.max(T_future_qs)
                            new_q = T_reward + DISCOUNT * T_max_future_q
                        else:
                            new_q = T_reward

                        T_current_qs[np.argmax(T_pred)] = new_q

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
                        print(f'Target updated at step {step}')

                    if step % SAVE_INTERVAL == SAVE_INTERVAL - 1:
                        torch.save(policy_net.state_dict(),
                                   f'nets/net_{step:07d}_{sum(losses) / len(losses):.8f}.pth')

                if done:
                    break

        if not done:
            history.extend(game_history)

        stats_training_loss = sum(losses) / len(losses) if len(losses) != 0 else 0
        stats_rewards = sum(rewards) / len(rewards) if len(rewards) != 0 else 0
        stats_wins = (sum(wins) / len(wins)) * 100 if len(wins) != 0 else 0

        print(f'Training loss: {stats_training_loss:.8f} | '
              f'Epsilon: {epsilon:.5f} | '
              f'Rewards: {stats_rewards:.5f} | '
              f'Wins: {stats_wins:.1f}% | '
              f'Memory size: {len(history)} ({MIN_HISTORY}-{MAX_HISTORY}) | '
              f'Steps: {step}')

        if len(history) >= MIN_HISTORY:
            writer.add_scalar('dqn/rewards', stats_rewards, step)
            writer.add_scalar('dqn/wins', stats_wins, step)
