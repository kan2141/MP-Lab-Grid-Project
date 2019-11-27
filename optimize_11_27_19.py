from gurobipy import *
import math
import numpy as np

#THESE ARE KNOWN VALUES OF P AND THETA
#P = [0.06898434531914893,-0.910892795686244,1.109422413867378,0.27946987882364516,-0.28053012083959555,-0.2664537214843326]
#Theta = [0,-3.24226423e-03, 2.78602061e-01, 1.69928719e+00, -8.24522246e-01, (4.20524401e+00-2*np.pi)]

#To solve for a value of P or Theta, remove it from the list below and write "[]" in its place
#For the most part, you can ignore this section and just look below at where it says "Create a New Model"
class ElecSys(object):
    
    def __init__(self):
        self.bus,   self.D, self.Theta, self.P= multidict({
            1:      [[1,0,0,0,0], 0.0, 0.06898434531914893],
            2:      [[-1,1,0,0,1], [], -0.910892795686244],
            3:      [[0,-1,1,1,0], [], []],
            4:      [[0,0,-1,0,0], 1.69928719e+00, 0.27946987882364516],
            5:      [[0,0,0,0,-1], [], []],
            6:      [[0,0,0,-1,0], (4.20524401e+00-2*np.pi), -0.2664537214843326]
        })
        # Resistence and reactance here are in Ohms 
        self.branch,    self.Zr,    self.Zx,    self.Y = multidict({
            (1,2):      [0.0922,    0.0470,     []],
            (2,3):      [0.4930,    0.2511,     []],
            (3,4):      [6.0499,    5.0835,     []],
            (3,6):      [10.4776,    8.8441,     []],
            (2,5):     [2.7866,    2.9276,     []]
        })
        self.Dt = {new_list: [] for new_list in range(1,len(self.D))}
        for k in self.Dt:
            l=k-1
            for i in range(len(self.D)):
                j=i+1
                self.Dt[k].append(self.D[j][l])

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

# Create variables
P = ElecSys.P.select('*')

Pstr = "P"
Thetastr = "Theta"
Pcount = 0
Thetacount = 0
Pmissing = [None]*len(ElecSys.P)
Thetamissing = [None]*len(ElecSys.Theta)
for i in ElecSys.bus:
    j=i-1
    if ElecSys.P[i]==[]:
        P[j] = m.addVar(lb = -GRB.INFINITY, ub=GRB.INFINITY, name = (Pstr + str(j)))
        Pmissing[Pcount] = j
        Pcount = Pcount + 1
    else:
        P[j] = ElecSys.P[i]
    if ElecSys.Theta[i]==[]:
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

Allmissing = [None]*len(ElecSys.P)
for i in range(len(ElecSys.bus)):
    if i in Pmissing:
        Allmissing[i] = i
    elif i in Thetamissing:
        Allmissing[i] = i
while None in Allmissing:
    Allmissing.remove(None)
    
ATheta = np.dot(A,Theta)
At = np.transpose(A)
Thetat = np.transpose(Theta)
##This is the first part of the equation: (1/2)*A*A'*Theta*Theta'
#part1 = np.dot((0.5),np.dot(np.dot(np.dot(A,At),Theta),Thetat))
##This is the second part of the equation: A'*P*Theta'
#part2 = np.dot(np.dot(At,P),Thetat)
##This shows the full equation that's being minimized
#part3 = np.subtract(part1,part2)
#print(part3)
lhseq = np.dot(np.dot(At,A),Theta)
rhseq = np.dot(At,P)

obj = LinExpr()
for i in range(len(P)):
    obj = obj + lhseq[i]-rhseq[i]
#obj = part1 - part2
m.setParam("PSDTol",5)
m.setObjective(obj,GRB.MINIMIZE)


#m.addConstr(lhseq,GRB.LESS_EQUAL,rhseq,name = "maybe")
#m.addQConstr(xtx,GRB.LESS_EQUAL,x2,name = "who knows")
#m.addQConstr(part1,GRB.EQUAL,part2,name="objconstr")
#m.addConstr(ATheta[2],GRB.LESS_EQUAL,P[2],name= "AThetaConstr")
Conststr = "PConstr"
for i in range(len(P)):
    m.addConstr(lhseq[i]<=rhseq[i],name= (Conststr+str(i)))
#Qstring = "QuadConstr"
#for i in Allmissing:
#    m.addQConstr(ATheta[i],GRB.LESS_EQUAL,P[i],name= (Qstring+str(i)))
m.optimize()
for v in m.getVars():
    print('%s %g' % (v.varName, v.x))

print('Obj: %g' % obj.getValue())
