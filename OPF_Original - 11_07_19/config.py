# Author: Jiang
# Parameters of the electric power system

from gurobipy import *
import math
import numpy as np

class Time(object):

    def __init__(self):
        self.serie = list(range(1,25))
        self.step = 60*60
        self.length = 24

class ElecSys(object):
    
    def __init__(self):
        self.baseMVA = 100
        self.baseKV = 12.66
        # Active and reactive loads here are in kW
        VolUB = 1.1**2
        VolLB = 0.9**2
        self.bus,   self.Pd,    self.Qd,    self.Vmax,  self.Vmin = multidict({
            1:      [0.0,       0.0,        1.0**2,     1.0**2],
            2:      [100.0,     60.0,       VolUB,      VolLB],
            3:      [330.0,      170.0,       VolUB,      VolLB],
            4:      [920.0,     950.0,       VolUB,      VolLB],
            5:      [360.0,      160.0,       VolUB,      VolLB],
            6:      [1075.0,      510.0,       VolUB,      VolLB]
        })
        # Resistence and reactance here are in Ohms 
        self.branch,    self.Zr,    self.Zx,    self.Imax = multidict({
            (1,2):      [0.0922,    0.0470,     GRB.INFINITY],
            (2,3):      [0.4930,    0.2511,     GRB.INFINITY],
            (3,4):      [6.0499,    5.0835,     GRB.INFINITY],
            (3,6):      [10.4776,    8.8441,     GRB.INFINITY],
            (2,5):     [2.7866,    2.9276,     GRB.INFINITY]
        })
        # Convert Pd and Qd from kW to MW
        for k in self.Pd:
            self.Pd[k] = self.Pd[k]/1e3
        for k in self.Qd:
            self.Qd[k] = self.Qd[k]/1e3
        # Convert Zr and Zx from ohms to pu
        Vbase = self.baseKV * 1e3
        Sbase = self.baseMVA * 1e6
        Zbase = Vbase**2/Sbase
        for k in self.Zr:
            self.Zr[k] = self.Zr[k] / Zbase
        for k in self.Zx:
            self.Zx[k] = self.Zx[k] / Zbase

# Power in MW/MVar, cost in $/MWh
class Gen(object):

    def __init__(self):
        # G1 denotes the main grid, and the cost coefficient is the electricity tariff.
        # G2 is a gas turbine with a efficiency of 40%. The gas price is 35.8 $/MWh.
        self.name,  self.bus,   self.cost,  self.Pmax,  self.Pmin,  self.DelPmax,   self.Qmax,  self.Qmin,  self.DelQmax \
        = multidict({
           # 'G1':   [1,         123.0,      0,         0,          5,              10,         -10,        10],
            'G2':   [2,         89.5,       2.0,        0.5,        0.5,            2.0,        -2.0,       1],
        })

class CoGen(object):

    def __init__(self):
        # C1 is a gas-fired combined heat and power plant. The heat and electricity efficiencies are 45% and 35%
        self.name,  self.bus,   self.cost,  self.Pmax,  self.Pmin,  self.DelPmax,   self.Qmax,  self.Qmin,  self.DelQmax, \
        self.node,  self.eff = multidict({
            'C1':   [2,         102.3,      4.0,        0.2,        1.0,            4.0,        -4.0,       2.0,     1,  1.286]
        })

class PhoArr(object):

    def __init__(self):
        self.name,  self.bus,   self.cost,  self.Pmax,  self.Pmin,  self.DelPmax,   self.Qmax,  self.Qmin,  self.DelQmax,   self.pf \
        = multidict({
            'P1':   [5,        0,          GRB.INFINITY,   0,      GRB.INFINITY,   GRB.INFINITY,   0,      GRB.INFINITY,   0.00],
            'P2':   [4,        0,          GRB.INFINITY,   0,      GRB.INFINITY,   GRB.INFINITY,   0,      GRB.INFINITY,   0.00]
        })

class WindTur(object):

    def __init__(self):
        self.name,  self.bus,   self.cost,  self.Pmax,  self.Pmin,  self.DelPmax,   self.Qmax,  self.Qmin,  self.DelQmax,   self.pf \
        = multidict({
            'W1':   [6,        0,          GRB.INFINITY,   0,      GRB.INFINITY,   GRB.INFINITY,   0,      GRB.INFINITY,   0.33],
            #'W2':   [25,        0,          GRB.INFINITY,   0,      GRB.INFINITY,   GRB.INFINITY,   0,      GRB.INFINITY,   0.33]
        })

class WatPump(object):

    def __init__(self):
        self.name,  self.bus,   self.cost,  self.Pmax,  self.Pmin,  self.DelPmax,   self.node,  self.eff = multidict({
            'WP1':  [2,         0,          20,         0,          4.0,            1,          0.85]
        })

class HeatPump(object):

    def __init__(self):
        self.name,  self.bus,   self.cost,  self.Pmax,  self.Pmin,  self.DelPmax,   self.node,  self.eff = multidict({
            'HP1':  [2,         0,          10,         0,        2.0,            1,          3.50]
        })
