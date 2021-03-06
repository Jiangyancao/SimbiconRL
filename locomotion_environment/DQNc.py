import gym
import math
import random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple
from itertools import count
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T


Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = torch.device("cpu")

class ReplayMemory(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *args):
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*args)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

#class DQN:
#    def __init__(self, session, input_size, output_size, name="main"):
#        self.session = session
#        self.input_size = input_size
#        self.output_size = output_size
#        self.net_name = name

    #    self._build_network()

    #def _build_network(self, h_size=10, l_rate=1e-1):
    #    wit

class DQN(nn.Module):

    def __init__(self):
        super(DQN, self).__init__()
        #self.conv1 = nn.Conv1d(3, 16, kernel_size=1)
        #self.bn1 = nn.BatchNorm1d(16)
        #self.conv2 = nn.Conv1d(16, 32, kernel_size=1)
        #self.bn2 = nn.BatchNorm1d(32)
        #self.conv3 = nn.Conv1d(32, 32, kernel_size=1)
        #self.bn3 = nn.BatchNorm1d(32)
        #self.head = nn.Linear(448, 2)
        self.head = nn.Linear(70,1024)
        self.n2 = nn.Linear(1024,512)
        self.n3 = nn.Linear(512,8)

    def forward(self, x):
        #x = F.relu(self.bn1(self.conv1(x)))
        #x = F.relu(self.bn2(self.conv2(x)))
        #x = F.relu(self.bn3(self.conv3(x)))
        print(x.dtype)
        #input("qabc")
        #print(self.head(x))
        x = F.relu(self.head(x))
        #print(x)
        #input("ggop")
        x = F.relu(self.n2(x))
        #print(x)
        #input("koko")
        #x = F.relu(self.n3(x))
        #print(x)
        #input("gggg")
        x.view(x.size(0), -1)
        #print(x)
        #input("qabc")
        x = F.relu(self.n3(x))
        #print(x)
        return x

BATCH_SIZE = 128
GAMMA = 0.999
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 400
TARGET_UPDATE = 10

policy_net = DQN().to(device)
target_net = DQN().to(device)
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = optim.RMSprop(policy_net.parameters())
memory = ReplayMemory(10000)

steps_done = 0





def select_action(state):
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * math.exp(-1* steps_done / EPS_DECAY)
    steps_done += 1
    #print(policy_net(state).max(1)[1].view(1,1));
    #input("gg")
    
    if sample > eps_threshold:
        with torch.no_grad():
            #print(policy_net(state))
            #input("gg")
            return policy_net(state)
    else:
        #input("rand")
        randi = np.array([random.uniform(0,1.0), random.uniform(0,1.0),random.uniform(0,1), random.uniform(0,1),random.uniform(0,1), random.uniform(0,1),random.uniform(0,1), random.uniform(0,1)])
        randi = torch.from_numpy(randi)
        randi.type(torch.DoubleTensor)
        #print(randi) 
        return randi
        #return torch.tensor(randi, device=device, dtype=torch.long)


def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)

    batch = Transition(*zip(*transitions))

    non_final_mask = torch.tensor(tuple(map(lambda s : s is not None, batch.next_state)),device = device, dtype = torch.uint8)
    
    #print(batch.next_state)
    #for s in batch.next_state:
    #    if s is not None:
            #print(s)
    #        non_final_n_states.cat([s])
    non_final_n_states = torch.cat([s for s in batch.next_state 
                                             if s is not None])

    state_batch = torch.cat(batch.state)

    #print(batch.state)
    #batch.action.type(torch.DoubleTensor)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)
    
    
    #print(action_batch)
    print(state_batch)
    #print(len(memory))
    state_batch = state_batch.reshape(128,70)
    action_batch = action_batch.reshape(128,8)
    state_action_values = policy_net(state_batch.float()).gather(1,action_batch.long())

    next_state_values = torch.zeros(BATCH_SIZE * 8, device =device)
    next_state_values = next_state_values.reshape(128, 8)
    non_final_n_states = non_final_n_states.reshape(128,70)
 
    print(len(non_final_mask))
    print(len(non_final_n_states))
    print(len(batch.next_state))
   
    next_state_values[non_final_mask] = target_net(non_final_n_states.float())

    print(next_state_values)
    reward_batch = reward_batch.reshape(128,8)
    expected_state_action_value = (next_state_values * GAMMA) + reward_batch

    loss = F.smooth_l1_loss(state_action_values, expected_state_action_value.unsqueeze(1))

    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()
