# 太阳帆运动模型搭建
import numpy as np
import matplotlib.pyplot as plt


class SolarSail_Max:

    def __init__(self, random=False):
        self.t = None  # 真实的时间
        self.td = None  # 按照天结算的时间
        self._state = None  # 内部运动学参数迭代过程
        self.state = None  # 观察变量
        self.random = random
        # 归一化参数长度除以AU,时间除以TU
        self.AU = 1.4959787 * (10 ** 11)
        self.mu = 1.32712348 * (10 ** 20)
        self.TU = np.sqrt(self.AU ** 3 / self.mu)
        self.constant = {'beta': 0.5 / 5.93, 'u0': 0, 'phi0': 0, 'r_f': 1.524, 'u_f': 0, 'phi_f': 0}
        self.constant['v_f'] = 1.0 / np.sqrt(self.constant['r_f'])
        # 特征加速度ac和光压因子beta或者说k的转换关系ac = 5.93beta
        self.delta_d = 1  # 仿真步长，未归一化，单位天
        self.delta_t = self.delta_d * (24 * 60 * 60) / self.TU  # 无单位
        self.reset()  # 初始化
        self.state_dim = len(self.state)
        self.action_dim = 5  # 五个初始变量需要猜测
        self.abound = np.array([-1*np.ones(self.action_dim), 1*np.ones(self.action_dim)]) # 动作空间的上下界

    def render(self):
        pass

    def reset(self):
        self.t = 0
        self.td = 0
        if self.random == True:
            rand_r0 = np.random.rand(1)
            self.constant['r0'] = (0.2 * rand_r0 + 1.0)[0]
            self.constant['v0'] = 1.0 / np.sqrt(self.constant['r0'])
        else:
            rand_r0 = 0.
            self.constant['r0'] = (0.2 * rand_r0 + 1.0)
            self.constant['v0'] = 1.0 / np.sqrt(self.constant['r0'])
        self._state = np.array([self.constant['r0'], self.constant['phi0'],
                                self.constant['u0'], self.constant['v0']])  # [r phi u v]
        self.state = np.array([self.constant['r0'], rand_r0])
        return self.state.copy()

    def step(self, action):
        # 传入五个协态变量
        # lambda1~4均是0-1的变量

        states_profile = np.empty((0, 4))  # 状态存储
        alpha_profile = np.empty((0, 1))  # 存储动作
        reward_profile = np.empty((0, 1))  # 存储奖励

        lambda_s = action[0:4] * 10  # 正负5之间
        td_f = action[4] * 250 + 350  # 100-600

        while True:
            # 根据协态变量初值求出最优控制量
            lambda1, lambda2, lambda3, lambda4 = lambda_s
            r, phi, u, v = self._state  # 当前状态的参数值
            if np.abs(lambda4) <= 0.0001:
                print('lambad4=', lambda4)
                if lambda3 <= 0:
                    alpha = 0
                else:
                    alpha = np.pi / 2
            else:
                alpha = np.arctan((-3 * lambda3 - np.sqrt(9 * lambda3 ** 2 + 8 * lambda4 ** 2)) / 4 / lambda4)
            # 进行积分求下一个状态
            if r > 0.001:
                r_dot = u
                phi_dot = v / r
                u_dot = self.constant['beta'] * ((np.cos(alpha)) ** 3) / (r ** 2) + \
                        (v ** 2) / r - 1 / (r ** 2)
                v_dot = self.constant['beta'] * np.sin(alpha) * (np.cos(alpha) ** 2) / (r ** 2) - u * v / r

                lambda1_dot = lambda2 * v / (r ** 2) + \
                              lambda3 * (2 * self.constant['beta'] * np.cos(alpha) ** 3 / (r ** 3) + \
                                         v ** 2 / (r ** 2) - 2 / (r ** 3)) + \
                              lambda4 * (2 * self.constant['beta'] * np.sin(alpha) * np.cos(alpha) ** 2 / (r ** 3) - \
                                         u * v ** 2 / r)
                lambda2_dot = 0
                lamnad3_dot = - lambda1 + lambda4 * v / r
                lambda4_dot = - lambda2 / r - 2 * lambda3 * v / r + lambda4 * u / r

                # 下一个状态
                self._state += self.delta_t * np.array([r_dot, phi_dot, u_dot, v_dot])  # [r,phi,u,v]
                lambda_s += self.delta_t * np.array([lambda1_dot, lambda2_dot, lamnad3_dot, lambda4_dot])
                self.td += self.delta_d
                self.t += self.delta_t
                states_profile = np.vstack((states_profile, self._state))
                alpha_profile = np.vstack((alpha_profile, alpha))
                if self.td >= td_f:
                    done = True
                    c1 = -200
                    c2 = -200
                    c3 = -200
                    reward = 30 - self.t + c1 * np.abs(self.constant['r_f'] - self._state[0]) + \
                             c2 * np.abs(self.constant['u_f'] - self._state[2]) + \
                             c3 * np.abs(self.constant['v_f'] - self._state[3])
                    break

            else:
                done = True
                reward = -10000
                break
        info = {}
        info['states_profile'] = states_profile
        info['alpha_profile'] = alpha_profile
        info['total_day'] = self.td
        info['rf_error'] = self._state[0] - self.constant['r_f']
        info['uf_error'] = self._state[2] - self.constant['u_f']
        info['vf_error'] = self._state[3] - self.constant['v_f']

        return self.state.copy(), reward, done, info


if __name__ == '__main__':
    env = SolarSail_Max()
    action = np.array([(-1.609601 + 5) / 10, (0.042179 + 5) / 10, \
                       (-0.160488 + 5) / 10, (-1.597537 + 5) / 10, (568 - 100) / 500])
    observation, reward, done, info = env.step(action)
    print(reward)

    states_profile = info['states_profile']
    alpha_profile = info['alpha_profile']

    plt.subplot(111, polar=True)
    theta = np.arange(0, 2 * np.pi, 0.02)
    plt.plot(theta, 1 * np.ones_like(theta), 'm')
    plt.plot(theta, 1.524 * np.ones_like(theta), 'b')
    plt.plot(states_profile[:, 1], states_profile[:, 0], 'r')

    plt.figure(2)
    plt.plot(states_profile[:, 0], 'm')
    plt.plot(env.constant['r_f'] * np.ones(len(states_profile[:, 0])))
    plt.title('r')

    plt.figure(3)
    plt.plot(states_profile[:, 2], 'm')
    plt.plot(env.constant['u_f'] * np.ones(len(states_profile[:, 0])))
    plt.title('v')
    plt.title('u')

    plt.figure(4)
    plt.plot(states_profile[:, 3], 'm')
    plt.plot(env.constant['v_f'] * np.ones(len(states_profile[:, 0])))
    plt.title('v')

    plt.figure(5)
    plt.plot(alpha_profile * 57.3, 'm')
    plt.title('alpha')

    plt.figure(6)
    plt.plot(info['reward_profile'], 'm')
    plt.title('reward')

    plt.show()
