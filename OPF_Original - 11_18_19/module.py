# Author: Jiang
# Module function for OPF

from gurobipy import *
import config as cf
import math    

# Creat an augmented dictionary with time index
# Duplicate input dict along the time horizon
def appendTime(x):
    # if the key of x is a tuple
    if isinstance(list(x.keys())[0], tuple):
        return {(t,i,j): x[i,j] for t in cf.Time().serie for (i,j) in x}
    else:
        return {(t,i): x[i] for t in cf.Time().serie for i in x}

# Create decision variables for CHPD model
def createVar(mod, PdDict, QdDict, PpvDict, QpvDict, PwtDict, QwtDict, PG2Dict, QG2Dict, PC1Dict, QC1Dict, VolDict, ThetaDict):
    # Import parameters and configuration
    Time = cf.Time() 
    ElecSys = cf.ElecSys()
    Gen = cf.Gen()
    CoGen = cf.CoGen()
    PhoArr = cf.PhoArr()
    WindTur = cf.WindTur()
    WatPump = cf.WatPump()
    HeatPump = cf.HeatPump()

    # Decision variables for electric power system
    Pflow = mod.addVars(Time.serie, ElecSys.branch, lb=0.0, ub=GRB.INFINITY, name='Pflow')
    Qflow = mod.addVars(Time.serie, ElecSys.branch, lb=0.0, ub=GRB.INFINITY, name='Qflow')

    BranCur = mod.addVars(Time.serie, ElecSys.branch, lb=0.0, ub=appendTime(ElecSys.Imax), name='BranCur')

    Pinje = mod.addVars(Time.serie, ElecSys.bus, lb=-GRB.INFINITY, ub=GRB.INFINITY, name='Pinje')
    Qinje = mod.addVars(Time.serie, ElecSys.bus, lb=-GRB.INFINITY, ub=GRB.INFINITY, name='Qinje')

    Vol = mod.addVars(Time.serie, ElecSys.bus, lb=appendTime(ElecSys.Vmin), ub=appendTime(ElecSys.Vmax), name='Vol')

    PGen = mod.addVars(Time.serie, Gen.name, lb=appendTime(Gen.Pmin), ub=appendTime(Gen.Pmax), name='PGen')
    QGen = mod.addVars(Time.serie, Gen.name, lb=appendTime(Gen.Qmin), ub=appendTime(Gen.Qmax), name='QGen')

    PCoGen = mod.addVars(Time.serie, CoGen.name, lb=appendTime(CoGen.Pmin), ub=appendTime(CoGen.Pmax), name='PCoGen')
    QCoGen = mod.addVars(Time.serie, CoGen.name, lb=appendTime(CoGen.Qmin), ub=appendTime(CoGen.Qmax), name='QCoGen')

    PPhoArr = mod.addVars(Time.serie, PhoArr.name, lb=appendTime(PhoArr.Pmin), ub=appendTime(PhoArr.Pmax), name='PPhoArr')
    QPhoArr = mod.addVars(Time.serie, PhoArr.name, lb=appendTime(PhoArr.Qmin), ub=appendTime(PhoArr.Qmax), name='QPhoArr')

    PWindTur = mod.addVars(Time.serie, WindTur.name, lb=appendTime(WindTur.Pmin), ub=appendTime(WindTur.Pmax), name='PWindTur')
    QWindTur = mod.addVars(Time.serie, WindTur.name, lb=appendTime(WindTur.Qmin), ub=appendTime(WindTur.Qmax), name='QWindTur')
                        
    PWatPump = mod.addVars(Time.serie, WatPump.name, lb=appendTime(WatPump.Pmin), ub=appendTime(WatPump.Pmax), name='PWatPump')

    PHeatPump = mod.addVars(Time.serie, HeatPump.name, lb=appendTime(HeatPump.Pmin), ub=appendTime(HeatPump.Pmax), name='PHeatPump')

    return Pflow, Qflow, BranCur, Pinje, Qinje, Vol, PGen, QGen, PCoGen, QCoGen, PPhoArr, QPhoArr, PWindTur, QWindTur, \
            PWatPump, PHeatPump

def CreateConstr(mod, PdDict, QdDict, PpvDict, QpvDict, PwtDict, QwtDict, PG2Dict, QG2Dict, PC1Dict, QC1Dict, VolDict, ThetaDict, \
                Pflow, Qflow, BranCur, Pinje, Qinje, Vol, PGen, QGen, PCoGen, QCoGen, PPhoArr, QPhoArr, PWindTur, QWindTur, \
                PWatPump, PHeatPump):
    # Import parameters and configuration
    Time = cf.Time() 
    ElecSys = cf.ElecSys()
    Gen = cf.Gen()
    CoGen = cf.CoGen()
    PhoArr = cf.PhoArr()
    WindTur = cf.WindTur()
    WatPump = cf.WatPump()
    HeatPump = cf.HeatPump()
    
    # Nodal power balance
    mod.addConstrs(( sum( [ PGen[t,j] for j in Gen.name if Gen.bus[j] == i ] ) + \
                    sum( [ PCoGen[t,j] for j in CoGen.name if CoGen.bus[j] == i ] ) + \
                    sum( [ PPhoArr[t,j] for j in PhoArr.name if PhoArr.bus[j] == i ] ) + \
                    sum( [ PWindTur[t,j] for j in WindTur.name if WindTur.bus[j] == i ] ) == \
                    sum( [ PWatPump[t,j] for j in WatPump.name if WatPump.bus[j] == i ] ) + \
                    sum( [ PHeatPump[t,j] for j in HeatPump.name if HeatPump.bus[j] == i ] ) + \
                    PdDict[t,i] + Pinje[t,i] \
                    for t in Time.serie for i in ElecSys.bus ), name='PNdBal')
    mod.addConstrs(( sum( [ QGen[t,j] for j in Gen.name if Gen.bus[j] == i ] ) + \
                    sum( [ QCoGen[t,j] for j in CoGen.name if CoGen.bus[j] == i ] ) + \
                    sum( [ QPhoArr[t,j] for j in PhoArr.name if PhoArr.bus[j] == i ] ) + \
                    sum( [ QWindTur[t,j] for j in WindTur.name if WindTur.bus[j] == i ] ) == \
                    QdDict[t,i] + Qinje[t,i] \
                    for t in Time.serie for i in ElecSys.bus ), name='QNdBal')
    # Ramping constraints
    
#    mod.addConstrs(( PGen[t,i]-PGen[t-1,i] <= Gen.DelPmax[i] \
#                    for t in Time.serie if (t-1) in Time.serie for i in Gen.name ), name='GenPRampMax')
#    mod.addConstrs(( PGen[t,i]-PGen[t-1,i] >= -Gen.DelPmax[i] \
#                    for t in Time.serie if (t-1) in Time.serie for i in Gen.name ), name='GenPRampMin')
#    mod.addConstrs(( QGen[t,i]-QGen[t-1,i] <= Gen.DelQmax[i] \
#                    for t in Time.serie if (t-1) in Time.serie for i in Gen.name ), name='GenQRampMax')
#    mod.addConstrs(( QGen[t,i]-QGen[t-1,i] >= -Gen.DelQmax[i] \
#                    for t in Time.serie if (t-1) in Time.serie for i in Gen.name ), name='GenQRampMin')
#    mod.addConstrs(( PCoGen[t,i]-PCoGen[t-1,i] <= CoGen.DelPmax[i] \
#                    for t in Time.serie if (t-1) in Time.serie for i in CoGen.name ), name='CoGenPRampMax')
#    mod.addConstrs(( PCoGen[t,i]-PCoGen[t-1,i] >= -CoGen.DelPmax[i] \
#                    for t in Time.serie if (t-1) in Time.serie for i in CoGen.name ), name='CoGenPRampMin')
#    mod.addConstrs(( QCoGen[t,i]-QCoGen[t-1,i] <= CoGen.DelQmax[i] \
#                    for t in Time.serie if (t-1) in Time.serie for i in CoGen.name ), name='CoGenQRampMax')
#    mod.addConstrs(( QCoGen[t,i]-QCoGen[t-1,i] >= -CoGen.DelQmax[i] \
#                    for t in Time.serie if (t-1) in Time.serie for i in CoGen.name ), name='CoGenQRampMin')
    mod.addConstrs(( PHeatPump[t,i]-PHeatPump[t-1,i] <= HeatPump.DelPmax[i] \
                    for t in Time.serie if (t-1) in Time.serie for i in HeatPump.name ), name='HPPRampMax')
    mod.addConstrs(( PHeatPump[t,i]-PHeatPump[t-1,i] >= -HeatPump.DelPmax[i] \
                    for t in Time.serie if (t-1) in Time.serie for i in HeatPump.name ), name='HPPRampMin')
    # Generation constraints of renewable energy 
    mod.addConstrs(( PPhoArr[t,i] <= PpvDict[t,i] for t in Time.serie for i in PhoArr.name ), name='PpvMax')
    mod.addConstrs(( PWindTur[t,i] <= PwtDict[t,i] for t in Time.serie for i in WindTur.name ), name='PwtMax')
    mod.addConstrs(( PGen[t,i] <= PG2Dict[t,i] for t in Time.serie for i in Gen.name ), name = 'PG2Max')
    mod.addConstrs(( QGen[t,i] <= QG2Dict[t,i] for t in Time.serie for i in Gen.name ), name = 'QG2Max')
    mod.addConstrs(( PCoGen[t,i] <= PC1Dict[t,i] for t in Time.serie for i in CoGen.name ), name = 'PC1Max')
    mod.addConstrs(( QCoGen[t,i] <= QC1Dict[t,i] for t in Time.serie for i in CoGen.name), name = 'QC1Max')
    mod.addConstrs(( PhoArr.pf[i] * PPhoArr[t,i] == QPhoArr[t,i] \
                    for t in Time.serie for i in PhoArr.name ), name='PVpf')
    mod.addConstrs(( WindTur.pf[i] * PWindTur[t,i] == QWindTur[t,i] \
                    for t in Time.serie for i in WindTur.name ), name='WTpf')
    # Branch flow model
    mod.addConstrs(( Pinje[t,j]/ElecSys.baseMVA == Pflow.sum(t,j,'*')/ElecSys.baseMVA - \
                    Pflow.sum(t,'*',j)/ElecSys.baseMVA + BranCur.prod(appendTime(ElecSys.Zr),t,'*',j) \
                    for t in Time.serie for j in ElecSys.bus ), name='BranPFlow')
    mod.addConstrs(( Qinje[t,j]/ElecSys.baseMVA == Qflow.sum(t,j,'*')/ElecSys.baseMVA - \
                    Qflow.sum(t,'*',j)/ElecSys.baseMVA + BranCur.prod(appendTime(ElecSys.Zx),t,'*',j) \
                    for t in Time.serie for j in ElecSys.bus ), name='BranQFlow')
    mod.addConstrs(( Vol[t,j] == Vol[t,i] - 2*(ElecSys.Zr[i,j]*Pflow[t,i,j]/ElecSys.baseMVA+ElecSys.Zx[i,j]*Qflow[t,i,j]/ElecSys.baseMVA) + \
                    (ElecSys.Zr[i,j]**2+ElecSys.Zx[i,j]**2)*BranCur[t,i,j] \
                    for t in Time.serie for (i,j) in ElecSys.branch ), name='VolEqu')
    mod.addConstrs(( Pflow[t,i,j]*Pflow[t,i,j] + Qflow[t,i,j]*Qflow[t,i,j] <= ElecSys.baseMVA**2*Vol[t,i]*BranCur[t,i,j] \
                    for t in Time.serie for (i,j) in ElecSys.branch ), name='RelaxBranFlow')         
