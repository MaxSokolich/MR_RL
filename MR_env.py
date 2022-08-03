#!/usr/bin/python
#-*- coding: utf-8 -*-

from gym import Env, spaces
import numpy as np
from shapely.geometry import LineString, Point
from MR_viewer import Viewer
from MR_data import MRExperiment
from MR_simulator import Simulator
from matplotlib import animation
import matplotlib.pyplot as plt
import gym 

"""
To do :
- Write Reward Function 
- 

"""
class MR_Env(Env):
    def __init__(self, type='continuous', action_dim = 2):
        self.type = type
        self.action_dim = action_dim
        # assert type == 'continuous' or type == 'discrete', 'type must be continuous or discrete'
        # assert action_dim > 0 and action_dim <=2, 'action_dim must be 1 or 2'
        self.action_space = spaces.Box(low=np.array([-100, -np.pi]), high=np.array([100, np.pi]))
        self.observation_space = spaces.Box(low=np.array([0,  0,0,  0, 0]), high=np.array([490, 490, 490, 490,8000]))
        self.init_space = spaces.Box(low=np.array([250, 250]), high=np.array([260, 260]))
        self.init_goal_space = spaces.Box(low=np.array([400, 400]), high=np.array([405, 405]))
        self.MR_data = None
        self.name_experiment = None
        self.last_pos = np.zeros(2)
        self.last_action = np.zeros(self.action_dim)
        self.init_goal = np.zeros(2)
        self.simulator = Simulator()
        self.number_loop = 0  # loops in the screen -> used to plot
        self.borders = [ [10, 490],[10, 10], [490,10], [490, 490]]
        self.viewer = None
        self.test_performance = False
        # self.init_test_performance = np.linspace(0, np.pi / 15, 10)
        self.counter = 0

        self.max_timesteps = 50
        self.min_dist2goal = 100


    def step(self, action):
        # According to the action stace a different kind of action is selected
        self.counter += 1
        action = action#*self.action_space.high
        f_t =  action[0]
        alpha_t = action[1]
        state_prime = self.simulator.step(f_t, alpha_t)

        # convert simulator states into observable states
        obs = self.convert_state(state_prime, self.init_goal) 
        done = self.end(state_prime=state_prime, obs=obs)
        rew = self.calculate_reward(obs=obs)

        self.last_pos = [state_prime[0], state_prime[1]]
        self.last_action = np.array([f_t ,alpha_t])

        if self.MR_data is not None:
            self.MR_data.new_transition(state_prime, obs, self.last_action, rew)
        info = dict()
        # print ("##############################################")
        # print ("\n action : ",self.last_action, "obs : ",obs,"rew : ",rew )
        return obs, rew, done, info

    def convert_state(self, state,goal_loc):
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
        x,y,goal_x,goal_y  = state[0], state[1], goal_loc[0], goal_loc[1]
        cur_loc = np.array((x,y))
        goal_loc = np.array((goal_x,goal_y))
        d = np.linalg.norm( goal_loc - cur_loc )
        obs = np.array([x,y, goal_x,goal_y ,d])
        return obs

    def calculate_reward(self, obs):
        x, y, d = obs[0], obs[1], obs[4]
        if d < self.min_dist2goal   :
            print("\n ############ Got there ########", d)
            return 5
        elif not self.observation_space.contains(obs) or self.counter > self.max_timesteps:
            # print("\n ############ hit wall ########", np.min([- 100.0,-d]))
            return -5
        else:
            return 0 # self.min_dist2goal  - d

    def end(self, state_prime, obs):
        """
        ? This method finds out whether we are at the end of episode
        """
        d = obs[4]
        if not self.observation_space.contains(obs) or self.counter > self.max_timesteps:
            # print("\n Smashed on wall")
            if self.viewer is not None:
                self.viewer.end_episode()
            if self.MR_data is not None:
                if self.MR_data.iterations > 0:
                    self.MR_data.save_experiment(self.name_experiment)
            return True
        elif d < self.min_dist2goal   :
            return True
        else:
            return False

    def set_init_space(self, low, high):
        self.init_space = spaces.Box(low=np.array(low), high=np.array(high))

    def set_goal(self,init):
        self.init_goal = self.init_goal_space.sample()
        while np.linalg.norm( self.init_goal - init ) < 50 :
            self.init_goal = self.init_space.sample()
        return np.array([400,400]) # self.init_goal

    def reset(self):
        init = self.init_space.sample()
        self.set_goal(init)
        self.simulator.reset_start_pos(init)
        self.goal_loc = self.init_space.sample()
        
        self.last_pos = init
        self.counter = 0
        # print('Reseting position')
        # print( "goal_loc ", self.goal_loc ,"init_pos",self.last_pos)
        state = self.simulator.get_state()
        if self.MR_data is not None:
            if self.MR_data.iterations > 0:
                self.MR_data.save_experiment(self.name_experiment)
            self.MR_data.new_iter(state, self.convert_state(state), np.zeros(len(self.last_action)), np.array([0]))
        if self.viewer is not None:
            self.viewer.end_episode()
        return self.convert_state(state,self.init_goal)

    def render(self, mode='human'):
        if self.viewer is None:
            self.viewer = Viewer()
            self.viewer.plot_boundary(self.borders)
            
        if 10 > self.number_loop: # ??
            self.viewer.end_episode()
            self.viewer.plot_position(self.last_pos[0], self.last_pos[1])
            self.viewer.restart_plot()
            self.number_loop += 1
        else:
            # self.viewer.plot_goal( self.init_goal, 2)
            self.viewer.plot_position(self.last_pos[0], self.last_pos[1])
            self.viewer.end_episode()
            self.viewer.restart_plot()


    def close(self, ):
        self.viewer.freeze_scream()

    def set_save_experice(self, name='experiment_ssn_ddpg_10iter'):
        assert type(name) == type(""), 'name must be a string'
        self.MR_data = MRExperiment()
        self.name_experiment = name

    def set_test_performace(self):
        self.test_performance = True





if __name__ == '__main__':

    """
    Ensure you have imagemagick installed with 
    sudo apt-get install imagemagick
    Open file in CLI with:
    xgd-open <filelname>
    """
    def save_frames_as_gif(frames, path='./', filename='gym_animation.gif'):

        #Mess with this to change frame size
        plt.figure(figsize=(frames[0].shape[1] / 72.0, frames[0].shape[0] / 72.0), dpi=72)

        patch = plt.imshow(frames[0])
        plt.axis('off')

        def animate(i):
            patch.set_data(frames[i])

        anim = animation.FuncAnimation(plt.gcf(), animate, frames = len(frames), interval=50)
        anim.save(path + filename, writer='imagemagick', fps=60)

    frames = []
    mode = 'normal'
    if mode == 'normal':
        env = MR_Env()
        shipExp = MRExperiment()
        for i_episode in range(5):
            observation = env.reset()
            for t in range(50):
                frames.append(env.render())
                # env.render()
                action = np.array([-2*t, np.pi*t/4])
                observation, reward, done, info = env.step(action)
                # print ("observation, reward, done, info \n")
                # print (observation, reward, done, info)
                if done:
                    print("Episode finished after {} timesteps".format(t + 1))
                    break
        env.close()
        save_frames_as_gif(frames)
        print("######### DONE ########")

