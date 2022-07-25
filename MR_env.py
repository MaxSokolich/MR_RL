#!/usr/bin/python
#-*- coding: utf-8 -*-

from gym import Env, spaces
import numpy as np
from shapely.geometry import LineString, Point
from MR_viewer import Viewer
from MR_data import MRExperiment
from MR_simulator import Simulator


"""
To do :
- Write Reward Function 
- 

"""
class MR_Env(Env):
    def __init__(self, type='continuous', action_dim = 2):
        self.type = type
        self.action_dim = action_dim
        self.dist2goal = 1000
        assert type == 'continuous' or type == 'discrete', 'type must be continuous or discrete'
        assert action_dim > 0 and action_dim <=2, 'action_dim must be 1 or 2'
        self.action_space = spaces.Box(low=np.array([-2, -180]), high=np.array([2, 180]))
        self.observation_space = spaces.Box(low=np.array([0,  0]), high=np.array([500, 500]))
        self.init_space = spaces.Box(low=np.array([100, 100]), high=np.array([100+10, 100+10]))

        self.MR_data = None
        self.name_experiment = None
        self.last_pos = np.zeros(2)
        self.last_action = np.zeros(self.action_dim)
        self.simulator = Simulator()
        self.start_pos = np.zeros(1)
        self.number_loop = 0  # loops in the screen -> used to plot
        self.borders = [ [0, 450],[0, 0], [450, 0], [450, 450]]
        self.viewer = None
        self.test_performance = False
        self.init_test_performance = np.linspace(0, np.pi / 15, 10)
        self.counter = 0
        self.goal_loc = np.array((0,0))
        self.min_dist2goal = 50


    def step(self, action):
        # According to the action stace a different kind of action is selected
        side1 = np.sign(self.last_pos[0])
        side2 = np.sign(self.last_pos[1])
        f_t =  action[0]*2#*side1
        alpha_t = action[1]*180#*side2
        
        state_prime = self.simulator.step(f_t, alpha_t)
        # convert simulator states into observable states
        obs = self.convert_state(state_prime) 
        done = self.end(state_prime=state_prime, obs=obs)
        rew = self.calculate_reward(obs=obs)

        self.last_pos = [state_prime[0], state_prime[1]]
        self.last_action = np.array([f_t ,alpha_t])
        if self.MR_data is not None:
            self.MR_data.new_transition(state_prime, obs, self.last_action, rew)
        info = dict()
        # print ("##############################################")
        print ("action : ",self.last_action, "obs : ",obs,"rew : ",rew )
        return obs, rew, done, info

    def convert_state(self, state):
        """
        This method generated the features used to build the reward function
        """
        # ship_point = Point((state[0], state[1]))
        # side = np.sign(state[1] - self.point_a[1])
        # d = ship_point.distance(self.guideline)  # meters
        # theta = side*state[2]  # radians
        # vx = state[3]  # m/s
        # vy = side*state[4]  # m/s
        # thetadot = side * state[5]  # graus/min
        # obs = np.array([d, theta, vx, vy, thetadot])
        return state

    def calculate_reward(self, obs):
        x, y = obs[0], obs[1]
        cur_loc = np.array((x, y))
        self.dist2goal = np.linalg.norm( self.goal_loc - cur_loc )
        if self.dist2goal < self.min_dist2goal   :
            # print("############ Got there ########")
            return 1000
        elif not self.observation_space.contains(obs):
            return - 1000
        else: 
            return - self.dist2goal

    def end(self, state_prime, obs):
        """
        ? This method finds out whether we are at the end of episode
        """
        if not self.observation_space.contains(obs):
            # print("\n Smashed on wall")
            if self.viewer is not None:
                self.viewer.end_episode()
            if self.MR_data is not None:
                if self.MR_data.iterations > 0:
                    self.MR_data.save_experiment(self.name_experiment)
            return True
        elif self.dist2goal < self.min_dist2goal   :
            return True
        else:
            return False

    def set_init_space(self, low, high):
        self.init_space = spaces.Box(low=np.array(low), high=np.array(high))

    def reset(self):
        init = list(map(float, self.init_space.sample()))
        self.simulator.reset_start_pos(init)
        self.last_pos = np.array(init)
        # print('Reseting position')
        state = self.simulator.get_state()
        if self.MR_data is not None:
            if self.MR_data.iterations > 0:
                self.MR_data.save_experiment(self.name_experiment)
            self.MR_data.new_iter(state, self.convert_state(state), np.zeros(len(self.last_action)), np.array([0]))
        if self.viewer is not None:
            self.viewer.end_episode()
        return self.convert_state(state)

    def render(self, mode='human'):
        if self.viewer is None:
            self.viewer = Viewer()
            self.viewer.plot_boundary(self.borders)
            self.viewer.plot_goal( self.goal_loc, 1)
        if 100 > self.number_loop: # ??
            self.viewer.end_episode()
            self.viewer.plot_position(self.last_pos[0], self.last_pos[1])
            self.viewer.restart_plot()
            self.number_loop += 1
        else:
            self.viewer.plot_position(self.last_pos[0], self.last_pos[1])

    def close(self, ):
        self.viewer.freeze_scream()

    def set_save_experice(self, name='experiment_ssn_ddpg_10iter'):
        assert type(name) == type(""), 'name must be a string'
        self.MR_data = MRExperiment()
        self.name_experiment = name

    def set_test_performace(self):
        self.test_performance = True

if __name__ == '__main__':
    mode = 'normal'
    if mode == 'normal':
        env = MR_Env()
        shipExp = MRExperiment()
        for i_episode in range(10):
            observation = env.reset()
            for t in range(2):
                env.render()
                action = np.array([10, 90])
                observation, reward, done, info = env.step(action)
                print ("observation, reward, done, info \n")
                print (observation, reward, done, info)
                if done:
                    print("Episode finished after {} timesteps".format(t + 1))
                    break
        env.close()