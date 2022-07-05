#!/usr/bin/python
#-*- coding: utf-8 -*-
import numpy as np
from scipy.integrate import RK45


class Simulator:
    def __init__(self):
        self.last_local_state = None
        self.current_action = None
        self.steps = 0
        self.time_span = 10           # 20 seconds for each iteration
        self.number_iterations = 100  # 100 iterations for each step
        self.integrator = None
        ##MR Constants
        self.a = 2

    def reset_start_pos(self, state_vector):
        x0, y0, vx0, vy0 = state_vector[0], state_vector[1], state_vector[2], state_vector[3]
        self.last_state = np.array([x0, y0, vx0, vy0])
        self.current_action = np.zeros(2)
        self.integrator = self.scipy_runge_kutta(self.simulate, self.get_state(), t_bound=self.time_span)

    def step(self, f_t, alpha_t):
        self.current_action = np.array([f_t, alpha_t])
        while not (self.integrator.status == 'finished'):
            self.integrator.step()
        self.last_state = self.integrator.y
        self.integrator = self.scipy_runge_kutta(self.simulate, self.get_state(), t0=self.integrator.t, t_bound=self.integrator.t+self.time_span)
        return self.last_state


    def simulate(self, states):
        """
        :param states: Space state
        :return df_states
        """
        x1 = states[0] #u
        x2 = states[1] #v
        x3 = states[2] #du
        x4 = states[3] #dv
        beta = self.current_action[0]*np.pi/6   #leme (-30 à 30)
        alpha = self.current_action[1]    #propulsor

        # Derivative function

        fx1 = x3
        fx2 = x4

        # simple model

        # main model simple -- > the best one:
        fx3 = self.a * beta  *np.cos(alpha)
        fx4 = self.a * beta  *np.sin(alpha)
        fx = np.array([fx1, fx2, fx3, fx4])
        return fx

    def scipy_runge_kutta(self, fun, y0, t0=0, t_bound=10):
        return RK45(fun, t0, y0, t_bound,  rtol=self.time_span/self.number_iterations, atol=1e-4)

    def runge_kutta(self, x, fx, n, hs):
        k1 = []
        k2 = []
        k3 = []
        k4 = []
        xk = []
        ret = np.zeros([n])
        for i in range(n):
            k1.append(fx(x)[i]*hs)
        for i in range(n):
            xk.append(x[i] + k1[i]*0.5)
        for i in range(n):
            k2.append(fx(xk)[i]*hs)
        for i in range(n):
            xk[i] = x[i] + k2[i]*0.5
        for i in range(n):
            k3.append(fx(xk)[i]*hs)
        for i in range(n):
            xk[i] = x[i] + k3[i]
        for i in range(n):
            k4.append(fx(xk)[i]*hs)
        for i in range(n):
            ret[i] = x[i] + (k1[i] + 2*(k2[i] + k3[i]) + k4[i])/6
        return ret

    def get_state(self):
        return self.last_state

