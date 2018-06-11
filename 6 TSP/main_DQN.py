import matplotlib.pyplot as plt
from D3QN import DQN
from TSP_Burma14 import ENV
import numpy as np

if __name__ == "__main__":
    env = ENV()
    RL = DQN(n_actions=env.action_dim,
             n_features=env.state_dim,
             learning_rate=0.001,
             gamma=0.90,
             e_greedy_end=0.1,
             e_greedy_init=0.8,
             memory_size=3000,
             e_liner_times=10000,
             units=10,
             batch_size=64,
             double=True,
             dueling=True,
             train=True if 1 == 1 else False
             )
    step = 0
    ep_reward = 0
    if RL.train:
        episodes = 20000
        for episode in range(episodes):
            ep_reward = 0
            # initial observation
            observation = env.reset()
            while True:
                env.render()
                action = RL.choose_action(observation)
                observation_, reward, done, info = env.step(action)
                ep_reward += reward
                RL.store_transition(observation, action, reward, observation_, done)
                if (step > 200) and (step % 5 == 0):
                    RL.learn()
                observation = observation_
                if done:
                    break
                step += 1
            print('Episode:', episode + 1, ' ep_reward: %.4f' % ep_reward, 'epsilon: %.3f' % RL.epsilon)
        RL.model_save()
    else:
        record = np.zeros([500, 2])
        record[0, 0] = env.city_location[0][0]
        record[0, 1] = env.city_location[0][1]
        # initial observation
        observation = env.reset()
        while True:
            env.render()
            action = RL.choose_action(observation)
            record[step + 1, 0] = env.city_location[action][0]
            record[step + 1, 1] = env.city_location[action][1]
            observation_, reward, done, info = env.step(action)
            print('reward', reward)
            ep_reward += reward
            observation = observation_
            for i in range(len(env.city_location)):
                plt.scatter(env.city_location[i][0], env.city_location[i][1])
                plt.text(env.city_location[i][0], env.city_location[i][1], str(i), size=15, alpha=0.2)
            plt.plot(record[:step + 2, 0], record[:step + 2, 1])
            plt.show()
            plt.pause(0.5)
            step += 1
            if done:
                record[step + 1, 0] = env.city_location[0][0]
                record[step + 1, 1] = env.city_location[0][1]
                for i in range(len(env.city_location)):
                    plt.scatter(env.city_location[i][0], env.city_location[i][1])
                    plt.text(env.city_location[i][0], env.city_location[i][1], str(i), size=15, alpha=0.2)
                plt.plot(record[:step + 2, 0], record[:step + 2, 1])
                plt.show()
                break
        print(' ep_reward: %.4f' % ep_reward)