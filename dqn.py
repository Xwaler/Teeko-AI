import torch
import torch.nn.functional as F
from torch.nn import Module, Conv2d, Linear


class Net(Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = Conv2d(3, 512, kernel_size=5, padding=3)
        self.linear1 = Linear(512 * 5 * 5, 256)
        self.linear2 = Linear(256, 5)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = x.view(-1, 512 * 5 * 5)
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x


class DQNAgent:
    def __init__(self):
        self.net = Net()
        self.net.load_state_dict(torch.load('net.pth'))

    def predict(self, state):
        with torch.no_grad():
            state = torch.from_numpy(state).unsqueeze(0).float()
            return self.net(state)[0].numpy()
