import random
import time

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from collections import deque

from mover.Mover import Mover
from scraper.Scraper import Scraper


class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 256)
        self.fc3 = nn.Linear(256, output_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


def select_action(state, policy_net, epsilon, action_space) -> int:
    if random.random() > epsilon:
        with torch.no_grad():
            return policy_net(state).argmax().item()
    else:
        return random.choice(action_space)


def optimize_model(policy_net, target_net, optimizer, memory, batch_size, gamma,device):
    if len(memory) < batch_size:
        return

    transitions = random.sample(memory, batch_size)
    batch_state, batch_action, batch_reward, batch_next_state, batch_done = zip(*transitions)


    batch_state = torch.stack(batch_state).to(device).squeeze(1)
    batch_action = torch.tensor(batch_action, dtype=torch.long).view(-1, 1).to(device)
    batch_reward = torch.tensor(batch_reward, dtype=torch.float32).to(device)
    batch_next_state = torch.stack(batch_next_state).to(device).squeeze(
        1)
    batch_done = torch.tensor(batch_done, dtype=torch.float32).to(device)

    current_q_values = policy_net(batch_state).gather(1, batch_action).squeeze(1)

    next_q_values = target_net(batch_next_state).max(1)[0]
    expected_q_values = batch_reward + (gamma * next_q_values * (1 - batch_done))

    loss = F.mse_loss(current_q_values, expected_q_values.detach())

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()


class Trainer(Scraper):
    def __init__(self, url: str, n_field: int):
        super().__init__(url, n_field)
        self.mover = Mover(self.browser)
        self.num_episodes = 1000
        self.output_dim = 4
        self.input_dim = 16
        self.load_model(DQN(input_dim=self.input_dim, output_dim=self.output_dim), "model.pth")

    def start(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        policy_net = DQN(input_dim=self.input_dim, output_dim=self.output_dim).to(self.device)
        target_net = DQN(input_dim=self.input_dim, output_dim=self.output_dim).to(self.device)
        target_net.load_state_dict(policy_net.state_dict())
        target_net.eval()
        optimizer = optim.Adam(policy_net.parameters(), lr=0.001)
        memory = deque(maxlen=10000)
        batch_size = 128
        gamma = 0.99
        epsilon_start = 1.0
        epsilon_end = 0.1
        epsilon_decay = 500
        target_update = 10
        self.train(policy_net, target_net, optimizer, memory, batch_size, gamma, epsilon_start, epsilon_end,
                   epsilon_decay, target_update)

    def train(self, policy_net, target_net, optimizer, memory, batch_size, gamma, epsilon_start, epsilon_end,
              epsilon_decay, target_update):
        for episode in range(self.num_episodes):
            state = self.reset()
            state = torch.tensor(state, dtype=torch.float32).view(1, -1)

            epsilon = epsilon_end + (epsilon_start - epsilon_end) * np.exp(-1. * episode / epsilon_decay)

            done = False
            total_reward = 0

            while not done:
                action = select_action(state, policy_net, epsilon, range(self.output_dim))
                next_state, reward = self.make_action(action)
                done = self.check_game_is_over()
                next_state = torch.tensor(next_state, dtype=torch.float32).view(1, -1)

                memory.append((state, action, reward, next_state, done))
                state = next_state

                total_reward += reward

                optimize_model(policy_net, target_net, optimizer, memory, batch_size, gamma, self.device)
            if episode % target_update == 0:
                target_net.load_state_dict(policy_net.state_dict())
            print(f"Episode {episode}: Total Reward: {total_reward}")
        self.save_model(policy_net, "model.pth")
    def save_model(self, model, path):
        torch.save(model.state_dict(), path)

    def load_model(self, model, path):

        try:
            model.load_state_dict(torch.load(path))
            model.eval()
        except:
            print("Model not found")
            self.save_model(model, path)
