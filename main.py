
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import torch.optim as optim

from classifier import LatticeClassification
from model import CustomDataset

torch.manual_seed(1337);
np.random.seed(1337);
grid_dataset = CustomDataset(2000);
grid_dataset_test = CustomDataset(100);

def train():
    net = LatticeClassification();
    net.train();
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    trainloader = DataLoader(grid_dataset, batch_size=50, shuffle=True, num_workers=0); 

    for epoch in range(100):  # loop over the dataset multiple times
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            # print(data);
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = data

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            loss = net.training_step((inputs, labels))
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()
        print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss/i}')
        running_loss = 0.0

    print('Finished Training, saving...')
    torch.save(net.state_dict(), "network.state")
    print('Evaluate')

def test():
    testloader = DataLoader(grid_dataset_test, batch_size=100, num_workers=0); 

    net = LatticeClassification();
    net.load_state_dict(torch.load("network.state"))
    net.eval();
    total = 0;
    correct = 0;
    with torch.no_grad():
        for i, data in enumerate(testloader, 0):
            inputs, labels = data;
            outputs = net(inputs);

            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    print(f"Network accuracy: {100*correct/total}%")

train();
# test();