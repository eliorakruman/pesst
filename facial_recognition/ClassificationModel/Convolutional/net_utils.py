import torch
import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # basic 3-layer structure
        self.conv_layer1 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=5, stride=1, padding=2)
        self.conv_layer2 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=5, stride=1, padding=2)
        self.pool = nn.MaxPool2d(kernel_size=2)
        # in_features is equivalent to channels * height * width
        # out_features should match number of possible data classes
        self.connected = nn.Linear(in_features=1568, out_features=512)
        self.connected2 = nn.Linear(in_features=512, out_features=2)

    def forward(self, data):
        # simple activation and pooling sequence
        data = self.pool(F.relu(self.conv_layer1(data)))
        data = self.pool(F.relu(self.conv_layer2(data)))
        data = data.view(data.size(0), -1)
        data = self.connected(data)
        data = self.connected2(data)
        return data
