#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.stats import gaussian_kde
import numpy as np
import argparse
import glob#, os
import sys
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Programa para graficar la distribución espacial de Q6.')
parser.add_argument('-f','--pfile',help='Input data file', required=False, action="store", default='q6')
parser.add_argument('-s','--skip', help='Skip data frames', type=int, required=False, action="store", default=1)
parser.add_argument('-g','--grid', help='Show grid', type=bool, required=False, action="store", default=False)
parser.add_argument('-y','--ymin', help='Min y-scale', type=float, required=False, action="store", default=0.0)
parser.add_argument('-Y','--ymax', help='Max y-scale', type=float, required=False, action="store", default=60.0)

args =  parser.parse_args()
preName = args.pfile + '_'
skp_frm = args.skip
show_grid = args.grid
scl_y_min = args.ymin
scl_y_max = args.ymax

fileFrames = []
# os.chdir('.')
for file in glob.glob(preName + '*.dat'):
    fileFrames.append(file)

#print fileFrames
fileFrames.sort()
n_file = 0
params = {'backend': 'pdf',
        'interactive': False,
        'lines.linewidth': 2.0,
        'axes.labelsize': 10,
        'font.size': 10,
        'legend.fontsize': 10,
        'xtick.labelsize': 15,
        'ytick.labelsize': 15,
        'figure.subplot.left':0.01,
        'figure.subplot.right':0.99,
        'figure.subplot.top':0.95,
        'figure.subplot.bottom':0.05,
        'text.usetex': True}
matplotlib.rcParams.update(params)

nTotFiles = len(fileFrames)
nActualFile = 0
colorG = []
maxY = []
#  fig, ax = plt.subplots()
for f in tqdm(fileFrames[::skp_frm]):
    fig = plt.figure(figsize=(10, 5))
    n_frame = (f.split('.')[0]).split('_')[1]
    ax=fig.add_subplot(121, aspect='equal')
    x, y, q6 = np.loadtxt(f, usecols=(1, 2, 3), unpack=True)
    xg = np.linspace(min(x), max(x), 100)
    yg = np.linspace(min(y), max(y), 300)
    X, Y = np.meshgrid(xg, yg)
    heatmap = griddata((x, y), q6, (X, Y), method='linear')  # Interpolación lineal
    # heatmap = griddata((x, y), q6, (X, Y), method='cubic')  # Interpolación cúbica
    im = ax.imshow(heatmap, extent=(min(x), max(x), min(y), max(y)), origin='lower', cmap='seismic')
    plt.colorbar(im)  # Agrega una barra de color para mostrar la escala de valores
    # plt.scatter(puntos[:, 0], puntos[:, 1], c=pf, cmap='hot', edgecolor='black')  # Muestra los puntos originales
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.grid(visible=show_grid, which='both')
    #  ax.axes.get_xaxis().set_visible(False)
    #  ax.axes.get_yaxis().set_visible(False)

    ax.set_ylim([scl_y_min,  scl_y_max])
    #  plt.ylim([yMin - 0.3 * alturaSilo,  1.1 * alturaSilo])
    # plt.ylim([yMin - 0.3 * alturaSilo, yMax + 0.15 * alturaSilo])
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$y$')
    ax.set_title(f'Heatmap $Q_6$ {n_frame}')

    ax2 =fig.add_subplot(122)
    ax2.set_title(f'KDE $Q_6$ {n_frame}')
    ax2.set_xlim([0, 1])
    ax2.set_xlabel(r"$Q_6$")
    ax2.set_ylim([0, 4])
    q_x = np.linspace(0, 1, 400)
    kde_q = gaussian_kde(q6)
    ax2.plot(q_x, kde_q(q_x))


    plt.tight_layout()
    plt.savefig(f'q6_{n_file:06d}.png')
    n_file += 1
    plt.close()

