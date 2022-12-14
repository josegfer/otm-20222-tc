#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 16:59:04 2022

@author: jose
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from paretoset import paretoset

def M(x):
    # _, count = np.unique(x, return_counts = True)
    # return np.sum(count * mpdb['m'].values)
    # ms = [m_rule[manutencao] for manutencao in x]
    # return np.sum(ms)
    return np.sum(x-1)

def weibull(t, eta, beta):
    return 1 - np.exp(-(t / eta) ** beta)

def prob(t_0, k, eta, beta, priori, deltat = 5):
    # priori = weibull(t_0, eta, beta) # this is constant
    return (weibull(t_0 + k * deltat, eta, beta) - priori) / (1 - priori)

def F(x):
    # k = [k_rule[manutencao] for manutencao in x]
    k = [(-x_i + 5) / 2 for x_i in x]
    p = [prob(t_0i, k_i, eta_i, beta_i, priori_i) for (t_0i, k_i, eta_i, beta_i, priori_i) in zip(t_0, k, eta, beta, priori)]
    return np.sum(p * f)

def F_ns(x):
    k = [(-x_i + 5) / 2 for x_i in x]
    p = [prob(t_0i, k_i, eta_i, beta_i, priori_i) for (t_0i, k_i, eta_i, beta_i, priori_i) in zip(t_0, k, eta, beta, priori)]
    return p * f

# read
equipdb = pd.read_csv('tc/EquipDB.csv', header = None, 
                      names = ['id', 't_0', 'cluster', 'f'])
mpdb = pd.read_csv('tc/MPDB.csv', header = None, 
                   names = ['id', 'k', 'm'])
clusterdb = pd.read_csv('tc/ClusterDB.csv', header = None, 
                        names = ['id', 'eta', 'beta'])

# dict
# m_rule = dict(enumerate(mpdb['m'], start = 1))
eta_rule = dict(enumerate(clusterdb['eta'], start = 1))
beta_rule = dict(enumerate(clusterdb['beta'], start = 1))
# k_rule = dict(enumerate(mpdb['k'], start = 1))

# custo constante
t_0 = equipdb['t_0'].values

cluster = equipdb['cluster'].values
eta = [eta_rule[i] for i in cluster]
beta = [beta_rule[i] for i in cluster]

priori = [weibull(t_0i, eta_i, beta_i) for (t_0i, eta_i, beta_i) in zip(t_0, eta, beta)]

f = equipdb['f'].values

# test eval
X = []

# selected
# esperado = priori * f
esperado = F_ns(x = np.ones(shape = 500))
importancia = np.argsort(esperado)

# alpha = 0.5555555555555555555555
# N = int(len(equipdb) * alpha)
# x = np.hstack((np.ones(shape = N), np.ones(shape = len(equipdb) - N) * 3))
# x = x[importancia.argsort()]
# print('M: {} | F: {}'.format(M(x), F(x)))
# X.append(x)
# sol_M = M(x)
# sol_F = F(x)

# num = 100
# alphas = np.linspace(start = 0.01, stop = 0.99, num = num)
# for alpha in alphas:
#     N = int(len(equipdb) * alpha)
#     x = np.hstack((np.ones(shape = N), np.ones(shape = len(equipdb) - N) * 3))
#     x = x[importancia.argsort()]
#     X.append(x)

# N = len(equipdb)
# alpha = 0.3
# gama = 0.4

# nenhuma = int(0.3 * N)
# intermediaria = int(0.4 * N)
# detalhada = 500 - nenhuma - intermediaria

# x = np.hstack((np.ones(shape = nenhuma), 
#                 np.ones(shape = intermediaria) * 2, 
#                 np.ones(shape = detalhada) * 3))
# x = x[importancia.argsort()]
# print('M: {} | F: {}'.format(M(x), F(x)))
# X.append(x)
# sol_M = M(x)
# sol_F = F(x)

N = len(equipdb)
num = 500
start = 0
stop = 1
log = []
alphas = np.linspace(start = start, stop = stop, num = num)
gamas = np.linspace(start = start, stop = stop, num = num)
for alpha in tqdm(alphas):
    for gama in gamas:
        if alpha + gama > 1:
            continue
        
        nenhuma = int(alpha * N)
        intermediaria = int(gama * N)
        detalhada = 500 - nenhuma - intermediaria
        
        x = np.hstack((np.ones(shape = nenhuma), 
                        np.ones(shape = intermediaria) * 2, 
                        np.ones(shape = detalhada) * 3))
        x = x[importancia.argsort()]
        X.append(x)
        log.append([M(x), F(x)])
hv = np.array([[report[-2], report[-1]] for report in log])

# # random
# x = np.random.choice(len(mpdb), len(equipdb)) + 1
# print('M: {} | F: {}'.format(M(x), F(x)))
# X.append(x)
# sol_M = M(x)
# sol_F = F(x)

# min M
x = np.ones(shape = 500)
print('M: {} | F: {}'.format(M(x), F(x)))
X.append(x)
# min_M = M(x)
# max_F = F(x)
log.append([M(x), F(x)])

# min F
x = np.ones(shape = 500) * 3
print('M: {} | F: {}'.format(M(x), F(x)))
X.append(x)
# max_M = M(x)
# min_F = F(x)
log.append([M(x), F(x)])

# filter
hv = np.array([[report[-2], report[-1]] for report in log])
mask = paretoset(hv, sense = ['min', 'min'])
pareto = hv[mask]

# export
export = pd.DataFrame(X).iloc[mask].astype('int32')
export.to_csv('tc/xhat.csv', header = False, index = False)

# # try predict s-metric
# ideal = (max_F - min_F) * (max_M - min_M)
# sol = (max_F - sol_F) * (max_M - sol_M)
# hv = sol / ideal
# print(hv)
