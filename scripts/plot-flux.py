#!/usr/bin/python3

import glob
import matplotlib.pyplot as plt
import numpy as np
import flujo

iFiles = []
for name in sorted(glob.glob('flx-00-*.dat')):
    iFiles.append(name)

mu = []
flx = []
t_fac = 0.01798809
m_g = 0.1319

for name in iFiles:
    n = name.split('-')
    print(name, n)
    mu.append(float(n[2][:3])/100)
    t, g = np.loadtxt(name, usecols=(0, 2), unpack=True)
    flx.append(flujo.flujo_masico(t, g, m=m_g))

plt.plot(mu, flx, 'o')

plt.xlabel(r"$\mu$")
plt.ylabel("Q (g/s)")
#  plt.legend()
plt.show()
