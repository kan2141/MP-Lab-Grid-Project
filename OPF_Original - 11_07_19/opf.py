# Author: Jiang
# Optimal power flow

from gurobipy import *
import numpy as np 
import matplotlib 
import matplotlib.pyplot as plt 
import pandas as pd 
import config as cf
import module as md
import math

def opf(PdDict, QdDict, PpvDict, QpvDict, PwtDict, QwtDict, PG2Dict, QG2Dict, PC1Dict, QC1Dict):
    # Import parameters and configuration
    Time = cf.Time() 
    ElecSys = cf.ElecSys()
    Gen = cf.Gen()
    CoGen = cf.CoGen()

    # Create optimization model
    mod = Model('OPF')
    
    # Create model variables
    Pflow, Qflow, BranCur, Pinje, Qinje, Vol, PGen, QGen, PCoGen, QCoGen, PPhoArr, QPhoArr, PWindTur, QWindTur, \
    PWatPump, PHeatPump = md.createVar(mod, PdDict, QdDict, PpvDict, QpvDict, PwtDict, QwtDict, PG2Dict, QG2Dict, PC1Dict, QC1Dict)

    # Create model constraints
    md.CreateConstr(mod, PdDict, QdDict, PpvDict, QpvDict, PwtDict, QwtDict, PG2Dict, QG2Dict, PC1Dict, QC1Dict, \
                    Pflow, Qflow, BranCur, Pinje, Qinje, Vol, PGen, QGen, PCoGen, QCoGen, PPhoArr, QPhoArr, PWindTur, QWindTur, \
                    PWatPump, PHeatPump )

    # Set objective
    obj = LinExpr()
    for t in Time.serie: 
        for i in Gen.name:
            obj = obj + PGen[t,i]*Gen.cost[i]
        for i in CoGen.name:
            obj = obj + PCoGen[t,i]*CoGen.cost[i]

    mod.setObjective(obj, GRB.MINIMIZE)

    # Output model
    mod.update()

    # Compute optimal solution
    mod.optimize()

    # Get optimized solutions
    Sol_PGen = mod.getAttr('X', PGen)
    Sol_PCoGen = mod.getAttr('X', PCoGen)
    Sol_PPhoArr = mod.getAttr('X', PPhoArr)
    Sol_PWindTur = mod.getAttr('X', PWindTur)
    Sol_PWatPump = mod.getAttr('X', PWatPump)
    Sol_PHeatPump = mod.getAttr('X', PHeatPump)
    Sol_Vol = mod.getAttr('X', Vol)
    Sol_BranCur = mod.getAttr('X', BranCur)
    Sol_Pflow = mod.getAttr('X', Pflow)
    Sol_Qflow = mod.getAttr('X', Qflow)

    # Display optimal solution
    plt.close('all')
    font = {'family' : 'sans-serif',
            'style' : 'normal',
            'weight' : 'bold',
            'size'   : 22}
    text = {'usetex' : True}
    matplotlib.rc('font', **font)
    matplotlib.rc('text', **text)
    
    # Active power balance of generation in a stacked bar graph
    plt.figure()
    width = 0.65
    plt.title('Active power balance: supply')
    #plt.bar(Time.serie, Sol_PGen.select('*','G1'), width, bottom=None, label=r'$P^{\rm{G}}_{1,t}$')
#    plt.bar(Time.serie, Sol_PGen.select('*','G2'), width, bottom=Sol_PGen.select('*','G1'), label=r'$P^{\rm{G}}_{2,t}$')
    plt.bar(Time.serie, Sol_PGen.select('*','G2'), width, bottom=None, label=r'$P^{\rm{G}}_{2,t}$')
    plt.bar(Time.serie, Sol_PCoGen.select('*','C1'), width, \
            #bottom=[sum(x) for x in zip(Sol_PGen.select('*','G1'),Sol_PGen.select('*','G2'))], label=r'$P^{\rm{C}}_{1,t}$')
            bottom=[sum(x) for x in zip(Sol_PGen.select('*','G2'))], label=r'$P^{\rm{C}}_{1,t}$')
    plt.bar(Time.serie, Sol_PPhoArr.select('*','P1'), width, \
#            bottom=[sum(x) for x in zip(Sol_PGen.select('*','G1'),Sol_PGen.select('*','G2'), \
#                                        Sol_PCoGen.select('*','C1'))], label=r'$P^{\rm{P}}_{1,t}$')
            bottom=[sum(x) for x in zip(Sol_PGen.select('*','G2'), \
                                        Sol_PCoGen.select('*','C1'))], label=r'$P^{\rm{P}}_{1,t}$')
    plt.bar(Time.serie, Sol_PWindTur.select('*','W1'), width, \
#            bottom=[sum(x) for x in zip(Sol_PGen.select('*','G1'),Sol_PGen.select('*','G2'), \
#                                        Sol_PCoGen.select('*','C1'),Sol_PPhoArr.select('*','P1'))], label=r'$P^{\rm{W}}_{1,t}$')
    bottom=[sum(x) for x in zip(Sol_PGen.select('*','G2'), \
                                        Sol_PCoGen.select('*','C1'),Sol_PPhoArr.select('*','P1'))], label=r'$P^{\rm{W}}_{1,t}$')
    plt.bar(Time.serie, Sol_PPhoArr.select('*','P2'), width, \
#            bottom=[sum(x) for x in zip(Sol_PGen.select('*','G1'),Sol_PGen.select('*','G2'), \
#                                        Sol_PCoGen.select('*','C1'),Sol_PPhoArr.select('*','P1'), \
#                                        Sol_PWindTur.select('*','W1'))], label=r'$P^{\rm{P}}_{2,t}$')
    bottom=[sum(x) for x in zip(Sol_PGen.select('*','G2'), \
                                        Sol_PCoGen.select('*','C1'),Sol_PPhoArr.select('*','P1'), \
                                        Sol_PWindTur.select('*','W1'))], label=r'$P^{\rm{P}}_{2,t}$')
    #plt.bar(Time.serie, Sol_PWindTur.select('*','W2'), width, \
     #       bottom=[sum(x) for x in zip(Sol_PGen.select('*','G1'),Sol_PGen.select('*','G2'), \
      #                                  Sol_PCoGen.select('*','C1'),Sol_PPhoArr.select('*','P1'), \
       #                                 Sol_PWindTur.select('*','W1'),Sol_PPhoArr.select('*','P2'))], label=r'$P^{\rm{W}}_{2,t}$')
    plt.legend()
    plt.xlabel('time $t$ (60-min step)')
    plt.ylabel('Power $P$ (MW)')
    plt.grid(linestyle='--')

    # Active power balance of loads in a stacked bar graph
    plt.figure()
    plt.title('Active power balance: demand')
    plt.bar(Time.serie, Sol_PWatPump.select('*','WP1'), width, bottom=None, label=r'$P^{\rm{WP}}_{1,t}$')
    plt.bar(Time.serie, Sol_PHeatPump.select('*','HP1'), width, bottom=Sol_PWatPump.select('*','WP1'), label=r'$P^{\rm{HP}}_{1,t}$')
    plt.bar(Time.serie, [sum([PdDict[t,j] for j in ElecSys.bus]) for t in Time.serie], width, \
            bottom=[sum(x) for x in zip(Sol_PWatPump.select('*','WP1'),Sol_PHeatPump.select('*','HP1'))], label=r'$P^{\rm{D}}_{t}$')
    Ploss = []
    for t in Time.serie:
        Ploss.append(-1*ElecSys.baseMVA*sum( [ElecSys.Zr[i,j]*Sol_BranCur[t,i,j] for (i,j) in ElecSys.branch] ))
    plt.bar(Time.serie, [-x for x in Ploss], width, \
            bottom=[sum(x) for x in zip(Sol_PWatPump.select('*','WP1'),Sol_PHeatPump.select('*','HP1'), \
                                        [sum([PdDict[t,j] for j in ElecSys.bus]) for t in Time.serie])], label=r'$P^{\rm{loss}}_{t}$')
    plt.legend()
    plt.xlabel('time $t$ (60-min step)')
    plt.ylabel('Power $P$ (MW)')
    plt.grid(linestyle='--')

    # Voltage profile
#    plt.figure()
#    plt.title('Voltage profile')
#    plt.step(Time.serie, Sol_Vol.select('*',1),'r-', where='mid', label='$v_{1}$')
#    plt.step(Time.serie, Sol_Vol.select('*',18),'b-', where='mid', label='$v_{18}$')
#    plt.step(Time.serie, Sol_Vol.select('*',22),'g-', where='mid', label='$v_{22}$')
#    plt.step(Time.serie, Sol_Vol.select('*',25),'k-', where='mid', label='$v_{25}$')
#    plt.step(Time.serie, Sol_Vol.select('*',33),'m-', where='mid', label='$v_{33}$')
#    plt.legend()
#    plt.xlabel('time $t$ (60-min step)')
#    plt.ylabel('Voltage $v$ (V)')
#    plt.grid(linestyle='--')

    plt.show()