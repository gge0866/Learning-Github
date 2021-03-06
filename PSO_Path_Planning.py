import numpy as np
import matplotlib.pyplot as plt
import control
import Catmull_Rom_splines as Cat
import implementation as Astar
import PathPlanning as PP
from scipy.integrate import odeint



# Getting the initial guess from A*
###############################################
# Implementing A*

precision=1
graph = Astar.GridWithWeights(15,15,precision)
start=(2,6)
goal=(10,6)
# start=(0,0)
# goal=(6,1)

# Define the boundaries of the obstacles
walls=[]


obstacle1_start=(6,3)
obstacle1_end=(14,5)


obstacle2_start=(6,5)
obstacle2_end=(9,7)


obstacle3_start=(6,7)
obstacle3_end=(12,10)

########################
# Constructing the obstacles

width1, height1 = PP.obstacle(obstacle1_start,obstacle1_end,walls,precision)

width2, height2 = PP.obstacle(obstacle2_start,obstacle2_end,walls,precision)

width3, height3 = PP.obstacle(obstacle3_start,obstacle3_end,walls,precision)


graph.walls=walls


# Define parameters for path planning
v=2
m=1                            # mass (kg)
k=(2*np.pi)**2             # spring constant (N/m)
c0=2*(m*k)**(1/2)
#zeta=0.1 lightly damped but it can get lower
zeta=0.0  # damping ratio
c=zeta*c0

param = [m, k, zeta]


came_from, cost_so_far = Astar.a_star_search(graph, start, goal, v, precision, param)

# I want to see the list of nodes that A* reconstructs
path=Astar.reconstruct_path(came_from, start, goal) #This should return the list of nodes for the path
# path.insert(0,start)
# path.append(goal)


cat_chain=Cat.CatmullRomChain(path, nPoints=500)
# print('cat_chain:',cat_chain)

######################
# From A* path planner

xc,yc=zip(*cat_chain) # points for catmull-rom spline
# vt=1
delta_t=0.025


path_length, duration, xc, yc, td = PP.distance(xc,yc,v,delta_t)

# t=np.arange(0,duration,delta_t) # simulation time to show residual vibration
t=np.arange(0,duration,delta_t) # simulation time to show residual vibration

# this will return the desired path of the flexible mode
xdp, delta_xd, delta_xd_dot = PP.reconst(xc,td,t,step=False)
ydp, delta_yd, delta_yd_dot = PP.reconst(yc,td,t,step=False)




# IDEA: Need to add length of solution to vibration amplitude produced by solution with weights
		# Use a good initial guess using A*
		# Prevent algorithm from accepting a worse design

# IDEA: Perturbations for distance should be set to exploit rather than explore
		# There is probably only one shortest path
		# Possibly want to modify shortest path to reduce some of the tracking error



class PSO:
	def __init__(self,start,goal,width,height,t,num_part):
		self.width=width
		self.height=height
		self.walls=[]
		self.particles=[] # this should have a shape of (num_part,3)
		self.v=[]
		self.best=None
		self.candidate_part=None # placeholder
		self.c1=0.01
		self.t=t
		self.desired=None


	def perterb(self,part,i):
		# This will perterb all three coordinates of a particle
		self.v[i] = self.c1 * (np.random.random_sample(3) - 0.5)
		return part + self.v[i] # candidate particle



	def move_particles(self):
		# allows the particles to be perterbed one at a time so that you can run obstacle detection
		i=0

		while i <= num_part-1:
			self.candidate_part[i] = self.perterb(self.particles[i],i)
			# self.particles[i]=candidate_part
			# i+=1

			if self.obs_detect() == False:
				# No obstacles detected
				i+=1

		current_cost = self.cost(start,goal)

		if current_cost <= self.best:
			print('Accepted new design.')
			# self.best_fv = error
			self.best = current_cost
			self.particles=self.candidate_part
			print('current_cost:',current_cost)

		else: # probability of accepting a worse design
			if (np.abs(current_cost-self.best))/self.best <= 0.00075 and np.random.random_sample()<=0.0075:
				self.particles=self.candidate_part
				self.best = current_cost
				print('Worse design accepted.')

			# Run the cost function
			# 	Cost function should have two functions
			# 	Cost for distance
			# 	Cost for vibration
			# Compare these costs with previous costs


	# def move_particles(self):
	# 	# allows the particles to be perterbed one at a time so that you can run obstacle detection
	# 	i=0

	# 	while i <= num_part-1:
	# 		candidate_part = self.perterb(self.particles[i],i)
	# 		# self.particles[i]=candidate_part
	# 		# i+=1

	# 		if self.obs_detect() == False:
	# 			# No obstacles detected
	# 			self.particles[i]=candidate_part
	# 			i+=1

	# 	length, error = self.cost(start,goal)

	# 	if length <= self.best_fd:
	# 		self.dbest=self.particles
	# 		self.best_fd = length

	# 		# Run the cost function
	# 			# Cost function should have two functions
	# 			# Cost for distance
	# 			# Cost for vibration
	# 		# Compare these costs with previous costs

	def obs_detect(self):
		# placeholder
		return False # no obstacle detected


	def cost(self,start,goal):
		# goal and start should not be particles that are perturbed
		xp=self.candidate_part[:,0]
		yp=self.candidate_part[:,1]
		time=self.t

		# define desired trajectory
		xd=self.desired[:,0]
		yd=self.desired[:,1]
		xd=np.insert(xd,0,start[0])
		xd=np.append(xd,goal[0])
		yd=np.insert(yd,0,start[1])
		yd=np.append(yd,goal[1])


		# add goal and start back into these arrays to calculate cost
		xp=np.insert(xp,0,start[0])
		xp=np.append(xp,goal[0])
		yp=np.insert(yp,0,start[1])
		yp=np.append(yp,goal[1])
		time=np.insert(time,0,0.0)


		# xp=self.particles[:,0]
		# yp=self.particles[:,1]

		part_length=np.sum(np.sqrt((xp[1:]-xp[0:-1])**2+(yp[1:]-yp[0:-1])**2))
		# di=np.sqrt((xp[1:]-xp[0:-1])**2+(yp[1:]-yp[0:-1])**2) # distance between each point on path
		# path_length=np.sum(di) # The actual length of the trajectory
		# sg_length=np.sqrt((goal[0]-xp[-1])**2+(goal[1]-yp[-1])**2) + np.sqrt((xp[0]-start[0])**2+(yp[0]-start[1])**2)
		# path_length = part_length + sg_length



		# parameters to calculate vibration
		zeta=0.0
		wn=2*np.pi
		wd = wn*np.sqrt(1-zeta**2)
		delta_xp=np.diff(xp)
		delta_yp=np.diff(yp)
		num_step=len(delta_xp)
		errors_sqx=np.zeros(num_step)
		errors_sqy=np.zeros(num_step)

		# time coordinate of each particle
		# position of each particle
		for i in range(num_step):
			# Error magnitude at each time step
			# errors_sqx[i] = (np.sum(delta_xp[0:i]*(np.exp(-zeta*wn*(t[i]-t[0:i]))*np.cos(wd*(t[i]-t[0:i]))-1))+xp[i])**2
			errors_sqx[i] = (np.sum(delta_xp[0:i]*(np.exp(-zeta*wn*(time[i]-time[0:i]))*np.cos(wd*(time[i]-time[0:i]))-1))+xd[i])**2
			# errors_sqy[i] = (np.sum(delta_yp[0:i]*(np.exp(-zeta*wn*(t[i]-t[0:i]))*np.cos(wd*(t[i]-t[0:i]))-1))+yp[i])**2
			errors_sqy[i] = (np.sum(delta_yp[0:i]*(np.exp(-zeta*wn*(time[i]-time[0:i]))*np.cos(wd*(time[i]-time[0:i]))-1))+yd[i])**2

		# mag_error=np.sqrt(errors_sqx+errors_sqy)
		# max_error=max(mag_error)
		meanerror=np.sum(errors_sqx+errors_sqy)/num_step
		# print('meanerror:',meanerror)
		# current_cost=0.0*part_length + 1.0*meanerror
		current_cost=1.0*meanerror
		# current_cost=0*part_length + 1.0*max_error
		# print('current_cost:',current_cost)

		# return part_length, meanerror
		return current_cost





# width=50
# height=50
width=15
height=15
# obs=[(2,4,2,4)] # Defines the corners of the obstacle
# start=(0,0)
# goal=(25,25)

# num_part=50

# xinit=np.linspace(start[0],goal[0],num_part)
# yinit=np.linspace(start[1],goal[1],num_part)
# tinit=np.linspace(0,0,num_part)

xinit=xdp
yinit=ydp
tinit=t
num_part=len(xinit)
# print('num_part:',num_part)
# print('len(t):',len(t))


run_PSO = PSO(start,goal,width,height,t,num_part)

run_PSO.particles=np.zeros((num_part,3))
run_PSO.particles[:,0]=xinit
run_PSO.particles[:,1]=yinit
run_PSO.particles[:,2]=tinit

run_PSO.desired=np.zeros((num_part,3))
run_PSO.desired[:,0]=xinit
run_PSO.desired[:,1]=yinit
run_PSO.desired[:,2]=tinit

# run_PSO.particles=np.random.random_sample((num_part,3))


# For now, just define attributes manually
run_PSO.v=np.zeros((num_part,3)) # to get initial perturbation
# run_PSO.dbest=np.zeros((num_part,3))
# run_PSO.vibest=np.zeros((num_part,3))
run_PSO.candidate_part=np.zeros((num_part,3))


# get initial costs
# run_PSO.best_fd,run_PSO.best_fv = run_PSO.cost(start,goal)
run_PSO.best = run_PSO.cost(start,goal)
print('Initial cost:',run_PSO.best)


num_iter=0
max_iter=5000
while num_iter<=max_iter: # If one of these conditions is broken, stop
	run_PSO.move_particles()
	# print(run_PSO.particles)


	# print('It ran!')
	# print('num_iter:',num_iter)
	num_iter+=1



xp=run_PSO.particles[:,0]
yp=run_PSO.particles[:,1]

xp, delta_xp, delta_xp_dot = PP.reconst(xp,td,t,step=False)
yp, delta_yp, delta_yp_dot = PP.reconst(yp,td,t,step=False)




def eq_of_motion(w, t, p):
    
    """
    Defines the differential equations for the coupled spring-mass system.

    Arguments:
        w :  vector of the state variables:
                  w = [x, y, x_dot, y_dot]
        t :  time
        p :  vector of the parameters:
                  p = [m, k, c, wf] # wf is forcing frequency
    
    Returns:
        sysODE : An list representing the system of equations of motion as 1st order ODEs
    """
    #x, x_dot = w
    x, x_dot, y, y_dot = w
    m, k, c, delta_xd, delta_yd, delta_xd_dot, delta_yd_dot = p

    # Create sysODE = (x', y', x_dot', y_dot'):
    # The state space equations


  
    sysODE = [x_dot,
              -k/m * x + k/m * command(delta_xd,td,t) - c/m * x_dot + c/m * command(delta_xd_dot,td,t),
              y_dot,
              -k/m * y + k/m * command(delta_yd,td,t) - c/m * y_dot + c/m * command(delta_yd_dot,td,t)]


    #sysODE = [x_dot,
    #          -k/m * x + k/m * xd(xc,td),
    #          y_dot,
    #          -k/m * y + k/m * yd(yc,td,t)]
    
    return sysODE

def command(delta_xd,td,t):
    xd=np.sum(delta_xd*(t>=td))
    return xd


# Set up simulation parameters
# ODE solver parameters
abserr = 1.0e-9
relerr = 1.0e-9
max_step = 0.001
#stoptime = max(time)+tp+10 #max time + tp is time of command, +10 allows plotting residual vibration
numpoints = 2501


# Initial conditions
x_init = xdp[0]                        # initial position
x_dot_init = 0.0                    # initial velocity
y_init = ydp[0]                    # initial angle
y_dot_init = 0.0                # initial angular velocity

#wf = np.sqrt(k / m1)                # forcing function frequency

# Pack the parameters and initial conditions into arrays 
p = [m, k, c, delta_xd, delta_yd, delta_xd_dot, delta_yd_dot]
x0 = [x_init, x_dot_init, y_init, y_dot_init]


# Call the ODE solver, returns the response of the system
resp1 = odeint(eq_of_motion, x0, t, args=(p,), atol=abserr, rtol=relerr,  hmax=max_step)

mean_error1, max_error1, mean_errorx1, mean_errory1, max_errorx1, max_errory1=PP.mean_max(resp1,duration,xdp,ydp,delta_t)
print('unmod_mean_error:',mean_error1)


p = [m, k, c, delta_xp, delta_yp, delta_xp_dot, delta_yp_dot]

resp2 = odeint(eq_of_motion, x0, t, args=(p,), atol=abserr, rtol=relerr,  hmax=max_step)

mean_error2, max_error2, mean_errorx2, mean_errory2, max_errorx2, max_errory2=PP.mean_max(resp2,duration,xdp,ydp,delta_t)
print('mod_mean_error:',mean_error2)



# plt.plot(xdp,ydp)
# plt.plot(xp,yp)
# # plt.plot(resp1[:,0],resp1[:,2])
# plt.plot(resp2[:,0],resp2[:,2])
fig = plt.figure(figsize=(6,4))
ax = plt.gca()
plt.subplots_adjust(bottom=0.17,left=0.17,top=0.96,right=0.96)
plt.setp(ax.get_ymajorticklabels(),family='serif',fontsize=18)
plt.setp(ax.get_xmajorticklabels(),family='serif',fontsize=18)
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.grid(True,linestyle=':',color='0.75')
ax.set_axisbelow(True)

obs1=plt.Rectangle(obstacle1_start,width1,height1,fc='0.75')
obs2=plt.Rectangle(obstacle2_start,width2,height2,fc='0.75')
obs3=plt.Rectangle(obstacle3_start,width3,height3,fc='0.75')
plt.gca().add_patch(obs1)
plt.gca().add_patch(obs2)
plt.gca().add_patch(obs3)

plt.plot(xdp,ydp,label='Desired',linestyle='-.',linewidth=2)
plt.plot(xp,yp,linestyle='-',linewidth=2,alpha=0)
plt.plot(resp1[:,0],resp1[:,2],label='Response',linestyle='-',linewidth=2)
plt.xlabel(r'X Position',family='serif',fontsize=22,weight='bold',labelpad=5)
plt.ylabel(r'Y Position',family='serif',fontsize=22,weight='bold',labelpad=10)
plt.xlim(2,16)
plt.ylim(0,18)
leg = plt.legend(loc='upper right', fancybox=True,ncol=1,borderaxespad=0.0, labelspacing=0.25)
ltext = leg.get_texts() 
plt.setp(ltext,fontsize=16)



fig = plt.figure(figsize=(6,4))
ax = plt.gca()
plt.subplots_adjust(bottom=0.17,left=0.17,top=0.96,right=0.96)
plt.setp(ax.get_ymajorticklabels(),family='serif',fontsize=18)
plt.setp(ax.get_xmajorticklabels(),family='serif',fontsize=18)
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.grid(True,linestyle=':',color='0.75')
ax.set_axisbelow(True)

obs1=plt.Rectangle(obstacle1_start,width1,height1,fc='0.75')
obs2=plt.Rectangle(obstacle2_start,width2,height2,fc='0.75')
obs3=plt.Rectangle(obstacle3_start,width3,height3,fc='0.75')
plt.gca().add_patch(obs1)
plt.gca().add_patch(obs2)
plt.gca().add_patch(obs3)

plt.plot(xdp,ydp,label='Desired',linestyle='-.',linewidth=2)
plt.plot(xp,yp,label='Input',linestyle='-',linewidth=2)
plt.plot(resp2[:,0],resp2[:,2],label='Response',linestyle='-',linewidth=2)
plt.xlabel(r'X Position',family='serif',fontsize=22,weight='bold',labelpad=5)
plt.ylabel(r'Y Position',family='serif',fontsize=22,weight='bold',labelpad=10)
plt.xlim(2,16)
plt.ylim(0,18)
leg = plt.legend(loc='upper right', fancybox=True,ncol=1,borderaxespad=0.0, labelspacing=0.25)
ltext = leg.get_texts() 
plt.setp(ltext,fontsize=16)



plt.show()





