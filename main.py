



import numpy as np
import sys
import Learning_module as GP # type: ignore
from utils import readfile, run_sim,test_gp,find_alpha_corrected
from utils import plot_xy,plot_traj,plot_vel
from scipy.ndimage import uniform_filter1d

# from MR_experiment import run_exp



# # if __name__ == "__main__":
# ### Start the code!
# case = "sim"

# time_steps =600
# actions = np.array([[1, np.pi*(2*(t/time_steps)-1)*(-1)**(t//600)] 
#                     for t in range(1,time_steps)]) # [T,action_dim]
# if case == "data": 
#     px,py,alpha,time,freq = readfile(r'D:/Projects/MMRs/Learning_Module/closedloopdata-10-1_withTIME/closed2.pickle')
#     todel = np.argwhere(alpha >= 500)
#     if len(todel) > 0:
#         todel = int(todel[0])
#         alpha = alpha[0:todel-1]
#         px = px[0:todel-1]
#         py = py[0:todel-1]
#         time = time[0:todel-1]
#     xys =[(px,py)]
#     legends =["data"]
    
#     # create a LearningModule object
#     gp = GP.LearningModule()
#     #train by passing in raw position + control signals as well as the time stamp
#     #note that freq is constant
#     a0 = gp.learn(px, py, alpha,freq, time)
#     print("Estimated a0 value is " + str(a0))
    
#     #this function plots what the GP has learned for each axis
#     gp.visualize()
# elif case == "sim":
#     px_sim,py_sim,alpha_sim,time_sim,freq_sim = run_sim(actions)
#     xys =[(px_sim,py_sim)]
#     legends =["simulation"]
#     gp_sim = GP.LearningModule()
#     a0_sim = gp_sim.learn(px_sim, py_sim, alpha_sim,freq_sim[0], time_sim)
#     print("Estimated a0 value is " + str(a0_sim))
#     gp_sim.visualize()
    
# elif case == "exp" :
#     px_exp,py_exp,alpha_exp,time_exp,freq_exp = run_exp(actions)
#     xys =[(px_exp,py_exp)]
#     legends =["exp"]
#     gp_exp = GP.LearningModule()
#     #train by passing in raw position + control signals as well as the time stamp
#     a0_exp = gp_exp.learn(px_exp, py_exp, alpha_exp,freq_exp[0], time_exp)
#     print("Estimated a0 value is " + str(a0_exp))
#     gp_exp.visualize()
# else: #get exp data and pass alphas to simulator
#     px,py,alpha,time,freq = readfile(r'D:/Projects/MMRs/Learning_Module/closedloopdata-10-1_withTIME/closed2.pickle')
#     todel = np.argwhere(alpha >= 500)
#     if len(todel) > 0:
#         todel   = int(todel[0])
#         alpha   = alpha[2:todel-1]
#         px      = px[2:todel-1]
#         py      = py[2:todel-1]
#         time    = time[2:todel-1]
    
#     freq_sim    = freq*np.ones(px.shape)/38
#     actions = np.array([[a,b] for a,b in zip(freq_sim,alpha)])
#     px_sim,py_sim,alpha_sim,time_sim,freq_sim = run_sim(actions,init_pos = np.array([px[0],py[0]]))

#     xys = [(px,py),(px_sim,py_sim)]
#     legends =["experiment","simulation"]

#     # create a LearningModule object
#     gp = GP.LearningModule()
#     gp_sim = GP.LearningModule()
#     #train by passing in raw position + control signals as well as the time stamp
#     #note that freq is constant
#     a0 = gp.learn(px, py, alpha, freq, time_sim)
#     a0_sim = gp_sim.learn(px_sim,py_sim,alpha_sim,freq_sim[0],time_sim)
#     print("Estimated a0 value is " + str(a0))
#     print("Estimated a0_sim value is " + str(a0_sim))
    
#     #this function plots what the GP has learned for each axis
#     gp.visualize()
#     gp_sim.visualize()
    
# plot_xy(xys,legends =legends)   

# ##########################################################
# ######################### TESTING ########################
# ##########################################################

# # read some more data and see how well we can predict
# time_steps = 40
# actions = np.array([[2, 0.1*np.pi*t**2] for t in range(1,time_steps)]) # [T,action_dim]

# px,py,alpha,time,freq = readfile(r'D:/Projects/MMRs/Learning_Module/closedloopdata-10-1_withTIME/closed.pickle')
# todel = np.argwhere(alpha >= 500)
# if len(todel) > 0:
#     todel   = int(todel[0])
#     alpha   = alpha[2:todel-1]
#     px      = px[2:todel-1]
#     py      = py[2:todel-1]
#     time    = time[2:todel-1]
# freq_sim    = freq*np.ones(px.shape)/38
# actions = np.array([[a,b] for a,b in zip(freq_sim,alpha)])
# px_sim,py_sim,alpha_sim,time_sim,freq_sim = run_sim(actions,init_pos = np.array([px[0],py[0]]))

# xys = [(px,py),(px_sim,py_sim)]
# legends =["experiment","simulation"]

# time = time_sim #time - time[0] #start at t=0 for readability of the final graph
# fig_title = ["experiment","simulation"]
# _,vxys1 = test_gp(gp,px,py,a0,alpha,freq,time)
# _,vxys2 = test_gp(gp_sim,px_sim,py_sim,a0_sim,alpha_sim,
#         freq_sim[0],time_sim)
# vxys = [vxys1,
#         vxys2]

# plot_xy(xys,legends =legends)   
# plot_vel(vxys,legends =legends) 
##########################################################
######################### Control ########################
##########################################################
time_steps =600
actions_learn = np.array([[1, np.pi*(2*(t/time_steps)-1)*(-1)**(t//600)] 
                        for t in range(1,time_steps)]) # [T,action_dim]

time_steps = 400
actions = np.array([[1, 0.3*np.pi*((t/time_steps)-1)*(-1)**(t//300)] 
                        for t in range(1,time_steps)]) # [T,action_dim]

noise_vars= [0.2,1.0,10]
a0_def = 1
for i in range(len(noise_vars)):
    # BASE_train: no noise, no learning
    px_base,py_base,alpha_base,time_base,freq_base = run_sim(actions_learn,
                                                             init_pos = np.array([0,0]),
                                                             noise_var = 0.0,a0=a0_def)
    # sim: noise, no learning
    px_sim,py_sim,alpha_sim, time_sim,freq_sim = run_sim(actions_learn,
                                                         init_pos = np.array([0,0]),
                                                         noise_var = noise_vars[i],a0=a0_def)
    # learn noise and a0
    gp_sim = GP.LearningModule()
    a0_sim = gp_sim.learn(px_sim, py_sim, alpha_sim,freq_sim[0], time_sim)
    print("Estimated a0 value is " + str(a0_sim))
    # gp_sim.visualize()
    xys  = [(px_base,py_base),
            (px_sim,py_sim),
           ]
    legends =["base (no noise)","sim with a0"
              ]
    fig_title   = ["Learn w and w/o noise"]
    plot_xy(xys,legends =legends,fig_title =["Learning traj w & w/o noise"]) 
    
    # BASE_test: no noise, no learning
    px_base,py_base,alpha_base,time_base,freq_base = run_sim(actions,
                                                             init_pos = np.array([0,0]),
                                                             noise_var = 0.0,
                                                             a0=a0_def)
    # sim: noise, no learning
    px_sim1,py_sim1,alpha_sim, time_sim,freq_sim = run_sim(actions,
                                                         init_pos = np.array([0,0]),
                                                         noise_var = noise_vars[i],
                                                         a0=a0_def)
    vd = np.zeros( (len(time_sim), 2) )
    v_pred = np.zeros( (len(time_sim), 2) )
    v_stdv  = np.zeros( (len(time_sim), 2) )
    
    actions_corrected = np.zeros(actions.shape)
    for ii in range(0, len(actions_corrected)):
        vd[ii,:] = a0_sim*freq_sim[0]*np.array( [np.cos(actions[ii,1]), np.sin(actions[ii,1])] ).reshape(1,-1)
        actions_corrected[ii,0] = actions[ii,0]
        actions_corrected[ii,1],muX, muY, sigX, sigY = find_alpha_corrected(vd[ii],gp_sim)
        v_pred[ii,0] = vd[ii,0]+muX
        v_pred[ii,1] = vd[ii,1]+muY
        v_stdv[ii,0] = sigX
        v_stdv[ii,1] = sigY
        
    
     # sim: noise, learning
    px_sim2,py_sim2,alpha_sim, time_sim,freq_sim = run_sim(actions_corrected,
                                                         init_pos = np.array([0,0]),
                                                         noise_var = noise_vars[i],
                                                         a0=a0_def)
    
    
    N = 5 #filter position data due to noisy sensing

    px_sim2 = uniform_filter1d(px_sim2, N, mode="nearest")
    py_sim2 = uniform_filter1d(py_sim2, N, mode="nearest")
    vx = np.gradient(px_sim2, time_sim)
    vy = np.gradient(py_sim2, time_sim)
    
    xys = [(px_base,py_base),
           (px_sim1,py_sim1),
        (px_sim2,py_sim2)]
    legends= ["base",
                "no learning ",
                "learning"]
    plot_xy(xys,legends =legends,fig_title =["Hello"]) 
    
    
    alphas = [(time_sim,actions[:,1]),
              (time_sim,actions_corrected[:,1]) ]
    
    plot_traj(alphas,legends =['alpha',
                                      'alpha_corrected'],fig_title =["alphas"])
    
    
    vxs = [(time_sim,vx),
            (time_sim,v_pred[:,0]+v_stdv[:,0]),
            (time_sim,v_pred[:,0]-v_stdv[:,0]),
            (time_sim,v_pred[:,0])]
    plot_traj(vxs,legends =['v_sim',
                                      'v_pred+',
                                      'v_pred-',
                                      'v_pred'],fig_title =["vel_X"])
    vys = [(time_sim,vy),
            (time_sim,v_pred[:,1]+v_stdv[:,1]),
            (time_sim,v_pred[:,1]-v_stdv[:,1]),
            (time_sim,v_pred[:,1])]
    plot_traj(vys,legends =['v_sim',
                                      'v_pred+',
                                      'v_pred-',
                                      'v_pred'],fig_title =["vel_Y"])
    
    
    # # time        = np.arange(1,time_steps) #start at t=0 for readability of the final graph
    # # alpha_sim   = actions[:,1]
    
    # # Case1: noise, noise correction
    # alpha_est1, vxys_1 =test_gp(gp_sim,px_sim,py_sim,
    #                      a0_def,alpha_sim,freq_sim[0],time_sim) # create a LearningModule object
    # v_desired1,v_error1,v_stdv,vx,vy = vxys_1
    # _,v_cmd1  = find_alpha_corrected(v_desired1,v_error1)# estimate correct alphas with default a0
    # actions1    = np.array([[1,alph ] for alph in alpha_est1]) # [T,action_dim]
    # px_c1,py_c1,_,_,_ = run_sim(actions1,
    #                             init_pos = np.array([0,0]),
    #                             noise_var = noise_vars[i],
    #                             a0=a0_def)
    
    # # Case3: noise, learned a0, learned error 
    # alpha_est2, vxys_2 = test_gp(gp_sim,px_sim,py_sim,
    #                      a0_sim,alpha_sim,freq_sim[0],time_sim) # create a LearningModule object
    # v_desired2,v_error2,v_stdv,vx,vy = vxys_2
    # _,v_cmd2 = find_alpha_corrected(v_desired2, v_error2)# estimate correct alphas with learned a0
    
    # actions2 = np.array([[1,alph] for alph in alpha_est2]) # [T,action_dim]
    # px_c2,py_c2,_,_,_ = run_sim(actions2,
    #                             init_pos = np.array([0,0]),
    #                             noise_var = noise_vars[i],
    #                             a0=a0_sim)
    
    # # Plot Control results 
    # xys  = [(px_base,py_base),
    #        (px_sim,py_sim),
    #        (px_c1,py_c1),
    #        (px_c2,py_c2)
    #        ]
    # v_sim = np.array([[i,j] for i,j in zip(vx,vy)])
    # alpha_sim_recovered,_= find_alpha_corrected(v_desired1, np.zeros(v_error1.shape))
    
    # alphas = [(time_sim,alpha_sim),
    #           (time_sim,alpha_sim_recovered),
    #        # (time_sim,alpha_est1),
    #        (time_sim,alpha_est2)
    #        ]
    
    # vxs = [(time_sim,v_sim[:,0]),
    #        (time_sim,v_cmd1[:,0]),
    #        (time_sim,v_cmd2[:,0])
    #        ]
    # vys = [(time_sim,v_sim[:,1]),
    #        (time_sim,v_cmd1[:,1]),
    #        (time_sim,v_cmd2[:,1])
    #        ]
    # v_errs = [(time_sim,v_error1[:,0]),
    #        (time_sim,v_error1[:,1]),
    #        (time_sim,v_error2[:,0]),
    #        (time_sim,v_error2[:,1])
    #        ]
    # vxys = [vxys_1,
    #         vxys_2
    #        ]
    
    # legends =["base (no noise)",
    #           "sim with a0",
    #           "w/noise correction",
    #           "w/noise correction + a0_learned"
    #           ]
    
    # fig_title   = ["TEST"]
    # plot_xy(xys,legends =legends,fig_title =["Trajectories"]) 
    # plot_traj(alphas,legends =['alpha_sim','alpha_sim_recovered',
    #                                   # 'alpha_cmd1',
    #                                   'alpha_cmd2'],fig_title =["alphas"])
    # # plot_traj(vxs, legends = ['v_sim', 'v_cmd1','v_cmd2'],fig_title =["x-velocities"])
    # # plot_traj(vys, legends = ['v_sim', 'v_cmd1','v_cmd2'],fig_title =["y-velocities"])
    # # plot_traj(v_errs, legends = ['v_errorX1', 'v_errorY1','v_errorX2','v_errorY2'],fig_title =["v-errors"])
    # # plot_vel([vxys_1],legends =['def a0'],fig_title =fig_title) 
    # plot_vel([vxys_2],legends =['learned a0'],fig_title =fig_title) 
    
    break
# v_desired,v_error,v_stdv,vx,vy = vxys_1