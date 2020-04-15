import torch
import torch.nn.functional as F
from torch.nn import Module, Conv2d, Linear, Sigmoid

from constants import DIRECTIONS


class Net(Module):
    def __init__(self):
        super(Net, self).__init__()
        self.linear1 = Linear(5 * 5, 1024)
        self.linear2 = Linear(1024, 1024)
        self.linear3 = Linear(1024, 35)
        self.sigmoid = Sigmoid()

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = self.sigmoid(self.linear3(x))
        return x


class DQNAgent:
    def __init__(self):
        self.net = Net()
        self.net.load_state_dict(torch.load('net.pth'))

    def predict(self, state):
        with torch.no_grad():
            state = torch.from_numpy(state).unsqueeze(0).float()
            return self.net(state)[0].numpy()

    @staticmethod
    def predsToMove(preds):
        move = [np.argmax(preds[:2]),
                np.argmax(preds[2:27]),
                DIRECTIONS[np.argmax(preds[27:35])]]
        return move

    @staticmethod
    def moveToPreds(move):
        preds = np.zeros(2 + 25 + 8, dtype=np.int8)
        preds[move[0]] = 1
        preds[2 + move[1]] = 1
        preds[2 + 25 + DIRECTIONS.index(move[2])] = 1
        return preds
