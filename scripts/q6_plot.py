#!/usr/bin/python3

import argparse
import glob
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
import numpy as np
from scipy.stats import gaussian_kde

parser = argparse.ArgumentParser(description="Ploteo de Q6 en una trayectoria.")
parser.add_argument("-t", "--title", help="Títle", required=True)

args = parser.parse_args()
title = args.title

iFiles = []
pasos = []
for name in sorted(glob.glob('q6_*.dat')):
    iFiles.append(name)
    n = name.split('_')
    pasos.append(int(n[1][:-4]))

print("Número de frames: ", len(iFiles))

n_puntos = 400
q_dominio = np.linspace(0, 1, n_puntos)
norm = mpl.colors.Normalize(vmin=min(pasos), vmax=max(pasos))
cmap = cm.cool
m = cm.ScalarMappable(norm=norm, cmap=cmap)


for name in iFiles:
    n = name.split('_')
    p = int(n[1][:-4])
    q = np.loadtxt(name, usecols=(3), unpack=True)
    kde_q = gaussian_kde(q)
    q_imagen = kde_q(q_dominio)
    plt.plot(q_dominio, q_imagen, c=m.to_rgba(p), alpha=0.5)

plt.title(title)
plt.xlabel(r"$Q_6$")
plt.ylabel(r"KDE($Q_6$)")
ca = plt.gca()
plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), label="Step")
plt.tight_layout()
plt.savefig("Q6_" + title + ".pdf")
