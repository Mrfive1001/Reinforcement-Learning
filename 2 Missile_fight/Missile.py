'''
Designed by MrFive
Environment like gym
'''

import time
import numpy as np


# np.random.seed(2)


class MissileAI:
    def __init__(self):
        near, mid, long, weixing, blood = 8, 5, 3, 1, 0
        self.init_state = np.array([near, mid, long, weixing, blood] * 2)  # 双方仓库导弹数目、卫星个数，血量
        self.state = self.reset()
        self.state_dim = len(self.state)  # 状态的维度是10
        self.action_dim = 15  # 动作的维度是15个值
        # self.hit = np.array([[[0.9, 0.7], [0.75, 0.5], [0, 0], [0, 0], [0, 0]],
        #                      [[0.8, 0.8], [0.7, 0.7], [0.7, 0.6], [0.7, 0.8], [0.5, 60]],
        #                      [[0.7, 0.9], [0.65, 0.8], [0.6, 0.75], [0.7, 0.7], [0.7, 100]]])
        self.hit = np.array([[[0.4, 0.4], [0.3, 0.4], [0.1, 0.4], [0, 0], [0, 0]],
                             [[0.5, 0.5], [0.4, 0.5], [0.4, 0.5], [0.7, 0.8], [0.4, 60]],
                             [[0.7, 0.6], [0.6, 0.6], [0.6, 0.6], [0.8, 0.8], [0.6, 100]]])
        # hit[i,j]第i个导弹命中j个地方的概率[命中率，损毁率]
        self.ip = 0.2  # 拦截率
        self.jump = int(self.state_dim / 2)  # 先后手区别的位数
        self.weixing_hit_help = 0.5  # 卫星起到提高命中率的作用
        self.weixing_stop_help = 3  # 卫星起到的拦截作用
        self.viewer = None  # 画图的作用

    def step(self, actions):
        action = np.zeros(4)
        action[0], action[1], action[2], action[3] = actions[0] // 5, actions[0] % 5, actions[1] // 5, actions[1] % 5
        action = [int(i) for i in action]
        a1 = action[0]  # 选手1选择的导弹
        t1 = action[1] + self.jump  # 选手1选择的目标
        a2 = action[2] + self.jump  # 选手2选择的导弹
        t2 = action[3]  # 选手2选择的目标

        weixing_add1 = (self.weixing_hit_help if self.state[3] > 0 else 0) + 1  # 卫星的加成
        weixing_add2 = (self.weixing_hit_help if self.state[8] > 0 else 0) + 1  # 卫星的加成

        base_ip1 = min(1, self.ip if (self.state[8] == 0 or t1 == 8) else self.ip * (1 + self.weixing_stop_help))
        base_ip2 = min(1, self.ip if (self.state[3] == 0 or t2 == 3) else self.ip * (1 + self.weixing_stop_help))
        hit_rate1, damage_rate1 = self.hit[action[0], action[1]]
        hit_rate2, damage_rate2 = self.hit[action[2], action[3]]

        flag_launch = {str(a1): 0, str(a2): 0}
        for missile in [a1, a2]:  # 先打出去一颗弹
            if self.state[missile] > 0:  # 如果有弹
                self.state[missile] -= 1  # 减少弹
                flag_launch[str(missile)] = 1
        # print((state_tem == self.state).all())

        state1 = self.state.copy()  # 为了先后手备份
        state2 = self.state.copy()
        reward1, reward2 = -1, -1  # 设置reward
        for missile, store, hit_rate, damage_rate, moon_add, state, reward, base_ip in zip(
                [a1, a2], [t1, t2], [hit_rate1, hit_rate2], [damage_rate1, damage_rate2]
                , [weixing_add1, weixing_add2], [state1, state2], [reward1, reward2], [base_ip1, base_ip2]):
            if flag_launch[str(missile)] == 1:  # 如果有弹
                # state[missile] -= 1  # 减少弹
                if np.random.rand(1) < (1 - base_ip):
                    if np.random.rand(1) < (hit_rate * moon_add):  # 命中
                        if store != 4 and store != 9:  # 命中非基地
                            tem = state[store]
                            for _ in range(tem):
                                if np.random.rand(1) < damage_rate:  # 损伤了
                                    state[store] -= 1
                        else:
                            state[store] -= damage_rate
            else:
                reward -= 0
        info = {}
        self.state = np.array([min(x, y) for x, y in zip(state1, state2)])
        if sum(self.state[:3]) + sum(self.state[self.jump:8]) == 0:  # 判断是否结束
            done = True
            damage1 = self.state[4] + np.random.rand(1)
            damage2 = self.state[9] + np.random.rand(1)
            reward = abs(int((damage1 - damage2) / 10))
            if damage1 > damage2:
                info['winner'] = 0
                reward1 += reward
                reward2 -= 0
            else:
                info['winner'] = 1
                reward1 -= 0
                reward2 += reward
            info['damage1'] = damage1
            info['damage2'] = damage2
        else:
            done = False
        return self.state.copy(), np.array([reward1, reward2]), done, info

    def reset(self):
        # 初始化状态
        self.state = self.init_state.copy()
        return self.state.copy()

    def robot_action(self, mode='rand_fool', first=True):
        # rand_fool
        # base_fool
        # rand_smart
        # base_smart
        if mode == 'rand_fool':  # 随机选动作，随机发炮
            return np.random.randint(3) * 5 + np.random.randint(5)
        elif mode == 'base_fool':  # 随机选择动作，瞄准基地
            return np.random.randint(3) * 5 + 4
        if first:
            mystate = self.state[:self.jump].copy()
            yourstate = self.state[self.jump:].copy()
        else:
            yourstate = self.state[:self.jump].copy()
            mystate = self.state[self.jump:].copy()  # 找出我方和敌方的不同状态
        if mode == 'rand_smart':  # 选择有弹的动作，随机打击对面非空仓库和基地
            missile = np.array([i for i in range(3) if mystate[i] != 0])
            if len(missile) == 0:
                return 0
            missile = np.random.choice(missile)
            store = [i for i in range(4) if yourstate[i] != 0]
            store.append(4)
            store = np.random.choice(store)
            return missile * 5 + store
        elif mode == 'base_smart':  # 选择有弹的动作，打击对面基地
            missile = np.array([i for i in range(3) if mystate[i] != 0])
            if len(missile) == 0:
                return 0
            missile = np.random.choice(missile)
            return missile * 5 + 4

    def render(self):
        pass
