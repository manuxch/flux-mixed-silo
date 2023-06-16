#!/usr/bin/env python3

import argparse
import glob
import matplotlib.pyplot as plt
import numpy as np
import flujo as fl

parser = argparse.ArgumentParser(description="Comparación experimental - simulación")
parser.add_argument("-e", "--exp", help="Archivo de datos experimentales", required=True)
parser.add_argument("-s", "--sim", help="Archivo de resultados de simulación", required=True)
parser.add_argument("-m", "--mu", help="muBase", required=True)
parser.add_argument("-d", "--diam", help="Diámetro del orificio de salida", required=True)

args = parser.parse_args()
fexp = args.exp
fsim = args.sim
muBase = args.mu
diam = args.diam

aex, fr, Lfr, Ufr = np.loadtxt(fexp, unpack=True)
Q = {}
for ang in aex:
    Q[int(ang)] = []

fin = open(fsim, "r")
data = fin.readlines()
fin.close()

angles = []
q_mean = []
q_max = []
q_min = []

for lin in data[1:]:
    l = lin.split()
    angles.append(int(l[0]))
    q = np.array([float(v) for v in l[1:]])
    q_mean.append(q.mean())
    q_max.append(q.max())
    q_min.append(q.min())

q_00 = q_mean[0]

q_mean /= q_00
q_max /= q_00
q_min /= q_00

q_max = np.abs(q_mean - q_max)
q_min = np.abs(q_mean - q_min)

print("# angle_deg Flow_rate_mean Low_err Up_err")
for a, qmean, qmax, qmin in zip(angles, q_mean, q_max, q_min):
    print(a, qmean, qmax, qmin)


errsim = [q_min, q_max]
errexp = [Lfr, Ufr]

aex = aex * np.pi / 180
an = np.array(angles) * np.pi / 180
alfa = 0.75
plt.errorbar(np.cos(aex), fr, yerr=errexp, marker='*', lw=0, elinewidth=1,
             capsize=5, label='Exp', alpha=alfa)
plt.errorbar(np.cos(an), q_mean, yerr=errsim, marker='o', lw=0, elinewidth=1,
             capsize=5, label='Sims', alpha=alfa)
plt.xlabel(r"$\cos \theta$")
plt.ylabel(r"$Q/Q_0$")
s_title = f"${diam} d$, $\mu_w = {muBase}$"
plt.title(s_title)
plt.legend()
plt.show()
