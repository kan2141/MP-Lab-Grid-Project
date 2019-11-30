from gurobipy import *
import math
import numpy as np

#THESE ARE KNOWN VALUES OF P AND THETA
#P = [0,-0.979877141005393,1.04043806854823,0.210485533504497,-0.349514466158744,-0.33543806680348]
#Theta = [0,-3.24226423e-03, 2.78602061e-01, 1.69928719e+00, -8.24522246e-01, (4.20524401e+00-2*np.pi)]

#To solve for a value of P or Theta, remove it from the list below and write "None" in its place
#Node 1 is the Slack Node, and if Theta or P data is missing, its value is zero
class ElecSys(object):
    
    def __init__(self):
        self.bus,   self.D, self.Theta, self.P= multidict({
            1:      [[1,0,0,0,0], None, None],
            2:      [[-1,1,0,0,1], -3.24226423e-03, None],
            3:      [[0,-1,1,1,0], 2.78602061e-01, 1.04043806854823],
            4:      [[0,0,-1,0,0], None, None],
            5:      [[0,0,0,0,-1], -8.24522246e-01, None],
            6:      [[0,0,0,-1,0], (4.20524401e+00-2*np.pi), None]
        })
        # Resistence and reactance here are in Ohms 
        self.branch,    self.Zr,    self.Zx,    self.Y = multidict({
            (1,2):      [0.0922,    0.0470,     []],
            (2,3):      [0.4930,    0.2511,     []],
            (3,4):      [6.0499,    5.0835,     []],
            (3,6):      [10.4776,    8.8441,     []],
            (2,5):     [2.7866,    2.9276,     []]
        })

ElecSys = ElecSys()
ElecSys.Bx = {}
count=0    
for i in ElecSys.branch:
    ElecSys.Bx[i] = 1 / ElecSys.Zx[i]
    count = count + 1
    if count > 1:
        for j in range(0,(count-1)):
            ElecSys.Y[i].append(0.0)
        ElecSys.Y[i].append(ElecSys.Bx[i])
        for j in range(0,(5-count)):
            ElecSys.Y[i].append(0.0)
    elif count == 1:
        ElecSys.Y[i].append(ElecSys.Bx[i])
        for j in range(0,4):
            ElecSys.Y[i].append(0.0) 

#Make matrices from dictionaries
D = np.array([ElecSys.D[i] for i in ElecSys.bus])
Dt = np.transpose(D)
Y = np.array([ElecSys.Y[i] for i in ElecSys.branch])
Theta = np.array([ElecSys.Theta[i] for i in ElecSys.bus])
A = np.dot(np.dot(D,Y),Dt)

# CREATE A NEW MODEL
m = Model("qp")

Pstr = "P"
Thetastr = "Theta"
Pcount = 0
Thetacount = 0
Pmissing = [None]*len(ElecSys.bus)
Thetamissing = [None]*len(ElecSys.bus)

#Go through the P and Theta vectors to determine which values are missing
for i in ElecSys.bus:
    j=i-1
    if ElecSys.P[i]==None:
        if j == 0:
            P[j] = 0
        elif j != 0 :
            P[j] = m.addVar(lb = -GRB.INFINITY, ub=GRB.INFINITY, name = (Pstr + str(j)))
            Pmissing[Pcount] = j
            Pcount = Pcount + 1
    else:
        P[j] = ElecSys.P[i]
    if ElecSys.Theta[i]==None:
        if j == 0:
            Theta[j] = 0
        elif j != 0:
            Theta[j] = m.addVar(lb = -GRB.INFINITY, ub=GRB.INFINITY, name = (Thetastr + str(j)))
            Thetamissing[Thetacount] = j
            Thetacount = Thetacount + 1
    else:
        Theta[j] = ElecSys.Theta[i]
while None in Pmissing:
    Pmissing.remove(None)
while None in Thetamissing:
    Thetamissing.remove(None)
m.update()

Allmissing = [None]*len(ElecSys.bus)
for i in range(len(ElecSys.bus)):
    if i in Pmissing:
        Allmissing[i] = i
    elif i in Thetamissing:
        Allmissing[i] = i
while None in Allmissing:
    Allmissing.remove(None)
    
#Set up the equations to optimize
#Multiply both sides of A*Theta = P by A transpose
At = np.transpose(A)
At_A_Theta = np.dot(np.dot(At,A),Theta)
At_P = np.dot(At,P)

#Minimize the error of At_A_Theta - At_P
obj = LinExpr()
for i in range(len(ElecSys.bus)):
    obj = obj + At_A_Theta[i]-At_P[i]
#m.setParam("PSDTol",5)
m.setObjective(obj,GRB.MINIMIZE)


#Create constraints
Conststr = "PConstr"
for i in range(len(ElecSys.bus)):
    m.addConstr(At_A_Theta[i]<=At_P[i],name= (Conststr+str(i)))

m.optimize()

#Print outputs
for v in m.getVars():
    print('%s %10.9g' % (v.varName, v.x))

print('Obj: %g' % obj.getValue())
