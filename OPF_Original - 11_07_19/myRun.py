import opf
import pandas as pd

# Import generation and load profiles
PdDF = pd.read_excel('Data.xlsx', sheet_name='Pd', index_col=0)
QdDF = pd.read_excel('Data.xlsx', sheet_name='Qd', index_col=0)
PpvDF = pd.read_excel('Data.xlsx', sheet_name='Ppv', index_col=0)
QpvDF = pd.read_excel('Data.xlsx', sheet_name='Qpv', index_col=0)
PwtDF = pd.read_excel('Data.xlsx', sheet_name='Pwt', index_col=0)
QwtDF = pd.read_excel('Data.xlsx', sheet_name='Qwt', index_col=0)
PG2DF = pd.read_excel('Data.xlsx', sheet_name='PG2', index_col=0)
QG2DF = pd.read_excel('Data.xlsx', sheet_name='QG2', index_col=0)
PC1DF = pd.read_excel('Data.xlsx', sheet_name='PC1', index_col=0)
QC1DF = pd.read_excel('Data.xlsx', sheet_name='QC1', index_col=0)

PdDict = { (t,c) : PdDF.to_dict('index')[t][c] for t in PdDF.index for c in PdDF.columns }
QdDict = { (t,c) : QdDF.to_dict('index')[t][c] for t in QdDF.index for c in QdDF.columns }
PpvDict = { (t,c) : PpvDF.to_dict('index')[t][c] for t in PpvDF.index for c in PpvDF.columns }
QpvDict = { (t,c) : QpvDF.to_dict('index')[t][c] for t in QpvDF.index for c in QpvDF.columns }
PwtDict = { (t,c) : PwtDF.to_dict('index')[t][c] for t in PwtDF.index for c in PwtDF.columns }
QwtDict = { (t,c) : QwtDF.to_dict('index')[t][c] for t in QwtDF.index for c in QwtDF.columns }
PG2Dict = { (t,c) : PG2DF.to_dict('index')[t][c] for t in PG2DF.index for c in PG2DF.columns }
QG2Dict = { (t,c) : QG2DF.to_dict('index')[t][c] for t in QG2DF.index for c in QG2DF.columns }
PC1Dict = { (t,c) : PC1DF.to_dict('index')[t][c] for t in PC1DF.index for c in PC1DF.columns }
QC1Dict = { (t,c) : QC1DF.to_dict('index')[t][c] for t in QC1DF.index for c in QC1DF.columns }

# Solve OPF
opf.opf(PdDict, QdDict, PpvDict, QpvDict, PwtDict, QwtDict, PG2Dict, QG2Dict, PC1Dict, QC1Dict)