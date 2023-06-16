#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.spatial import Voronoi, ConvexHull
import numpy as np
import argparse
import glob#, os
from tqdm import tqdm

def voronoi_volumes(points):
    v = Voronoi(points)
    vol = np.zeros(v.npoints)
    for i, reg_num in enumerate(v.point_region):
        indices = v.regions[reg_num]
        if -1 in indices: # some regions can be opened
            vol[i] = np.inf
        else:
            vol[i] = ConvexHull(v.vertices[indices]).volume
    return vol

def packing_fraction(points, radii):
    vol = voronoi_volumes(points)
    pf = np.zeros(points.shape[0])
    for i, p in enumerate(puntos):
        pf[i] = np.pi * radii[i]**2 / vol[i]
    return pf

parser = argparse.ArgumentParser(description='Programa para graficar la distribución espacial de PF.')
parser.add_argument('-f','--pfile',help='Input data file', required=False, action="store", default='frm')
parser.add_argument('-s','--skip', help='Skip data frames', type=int, required=False, action="store", default=1)
parser.add_argument('-g','--grid', help='Show grid', type=bool, required=False, action="store", default=False)
parser.add_argument('-y','--ymin', help='Min y-scale', type=float, required=False, action="store", default=-5.0)
parser.add_argument('-Y','--ymax', help='Max y-scale', type=float, required=False, action="store", default=20.0)

args =  parser.parse_args()
preName = args.pfile + '_'
skp_frm = args.skip
show_grid = args.grid
scl_y_min = args.ymin
scl_y_max = args.ymax

fileFrames = []
# os.chdir('.')
for file in glob.glob(preName + '*.xy'):
    fileFrames.append(file)

#print fileFrames
fileFrames.sort()

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
for f in tqdm(fileFrames[::skp_frm]):
    fig = plt.figure(figsize=(10,10))
    n_frame = (f.split('.')[0]).split('_')[1]
    ax=fig.add_subplot(111, aspect='equal')
    idd = []
    x = []
    y = []
    r = []
    fin = open(f, "r")
    data = fin.readlines()
    fin.close()
    for linea in data:
        l = linea.split()
        if int(l[0]) > 0:
            idd.append(int(l[0]))
            x.append(float(l[2]))
            y.append(float(l[3]))
            r.append(float(l[4]))
    puntos = np.stack((x,y), axis=1)
    pf = packing_fraction(puntos, r)
    fout = open('pf_' + n_frame + '.dat', 'w')
    fout.write(f"# Frame: {n_frame}\n")
    fout.write(f"# id x y pf\n")
    for i in range(len(x)):
        sout = f"{idd[i]} {x[i]} {y[i]} {pf[i]}\n"
        fout.write(sout)
    fout.close()
    xg = np.linspace(min(x), max(x), 100)
    yg = np.linspace(min(y), max(y), 300)
    X, Y = np.meshgrid(xg, yg)
    heatmap = griddata((x, y), pf, (X, Y), method='linear')  # Interpolación lineal
    # heatmap = griddata((x, y), q6, (X, Y), method='cubic')  # Interpolación cúbica
    plt.imshow(heatmap, extent=(min(x), max(x), min(y), max(y)), origin='lower', cmap='Greens')
    plt.colorbar()  # Agrega una barra de color para mostrar la escala de valores
    # plt.scatter(puntos[:, 0], puntos[:, 1], c=pf, cmap='hot', edgecolor='black')  # Muestra los puntos originales
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.grid(visible=show_grid, which='both')
    #  ax.axes.get_xaxis().set_visible(False)
    #  ax.axes.get_yaxis().set_visible(False)

    plt.ylim([scl_y_min,  scl_y_max])
    #  plt.ylim([yMin - 0.3 * alturaSilo,  1.1 * alturaSilo])
    # plt.ylim([yMin - 0.3 * alturaSilo, yMax + 0.15 * alturaSilo])
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(f'Heatmap pf {n_frame}')
    plt.tight_layout()
    plt.savefig('pf_' + n_frame + '.png')
    plt.close()

