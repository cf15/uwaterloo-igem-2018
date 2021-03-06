#Michael Astwood 2018 with help from https://apmonitor.com/wiki/index.php/Main/GekkoPythonOptimization
#This program is built to control light
#levels based on data taken during experiments.

from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt

m = GEKKO()
m.time = np.linspace(0,20,41)

# Parameters for model
mass = 500
b = m.Param(value=50)
K = m.Param(value=0.8)

# Manipulated variable (in our system it will be the light intensity)
p = m.MV(value=50, lb=0, ub=100) #value is initial value, ub is upper bound, lb is lower bound
p.STATUS = 1  # allow optimizer to change
p.DCOST = 0 # smooth out changes in intensity
p.DMAX = 10   # slow down changes in intensity

# Controlled Variable (in our system it will be the ratio)
v = m.CV(value=0)
v.STATUS = 1            # add the setpoint to the objective
m.options.CV_TYPE = 2   # squared error root(sum(x^2))
v.SP = 40               # set point
v.TR_INIT = 0           # set point trajectory (0 = straight line at SP, 1 = starts at zero and ramps up)
v.TAU = 5               # time constant of trajectory

# Process model (this is a model for car acceleration)
m.Equation(mass*v.dt() == -v*b + K*b*p) #a differential equation in terms of our controlled variable
#linear drag vs gas pedal input

m.options.IMODE = 6 #this puts the library in MPC mode
m.solve(disp=True) #this finalizes our controller for this prediction cycle

# get additional solution information
import json
with open(m.path+'//results.json') as f:
    results = json.load(f)

#plotting the results
plt.figure()
plt.subplot(2,1,1)
plt.plot(m.time,p.value,'b-',label='MV Optimized')
plt.legend()
plt.ylabel('Input')
plt.subplot(2,1,2)
plt.plot(m.time,results['v1.tr'],'k-',label='Reference Trajectory')
plt.plot(m.time,v.value,'r--',label='CV Response')
plt.ylabel('Output')
plt.xlabel('Time')
plt.legend(loc='best')
plt.show()
