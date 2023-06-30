#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.spatial import Voronoi, ConvexHull, voronoi_plot_2d
from scipy.stats import gaussian_kde
import numpy as np
import argparse
import glob#, os
from tqdm import tqdm

def voronoi_volumes(points, i):
    v = Voronoi(points)
    ffig = voronoi_plot_2d(v, show_vertices=False, line_colors='orange',
                           line_width=2, line_alpha=0.6, point_size=2)
    plt.savefig('v2s-'+str(i)+'.png')
    plt.close(ffig)
    vol = np.zeros(v.npoints)
    for i, reg_num in enumerate(v.point_region):
        indices = v.regions[reg_num]
        if -1 in indices: # some regions can be opened
            vol[i] = np.inf
        else:
            try:
                vol[i] = ConvexHull(v.vertices[indices]).volume
            except:
                print("Falla de cálculo de ConvexHull")
                vol[i] = np.inf
    return vol

def packing_fraction(points, radii, i):
    vol = voronoi_volumes(points, i)
    pf = np.zeros(points.shape[0])
    for i in range(points.shape[0]):
        pf[i] = np.pi * radii[i]**2 / vol[i]
        # print(f"i: {i}, {points[i]}, r: {radii[i]}, vp: {np.pi* radii[i]**2}, vv: {vol[i]}, pf: {pf[i]}")
    return pf

parser = argparse.ArgumentParser(description='Programa para graficar la distribución espacial de PF.')
parser.add_argument('-f','--pfile',help='Input data file', required=False, action="store", default='frm')
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
n_png = 0
for f in tqdm(fileFrames[::skp_frm]):
    fig = plt.figure(figsize=(10,5))
    n_frame = (f.split('.')[0]).split('_')[1]
    ax=fig.add_subplot(121, aspect='equal')
    idd = []
    tipo = []
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
            tipo.append(int(l[1]))
            x.append(float(l[2]))
            y.append(float(l[3]))
            r.append(float(l[4]))
    puntos = np.stack((x,y), axis=1)
    pf = packing_fraction(puntos, r, n_frame)
    fout = open('pf_' + n_frame + '.dat', 'w')
    fout.write(f"# Frame: {n_frame}\n")
    fout.write(f"# id x y pf\n")
    for i in range(len(x)):
        # if pf[i] > 1:
            # print(f"i: {i}, tipo: {tipo[i]}, x: {x[i]} y: {y[i]} pf: {pf[i]}")
        sout = f"{idd[i]} {x[i]} {y[i]} {pf[i]}\n"
        fout.write(sout)
    fout.close()
    xg = np.linspace(min(x), max(x), 100)
    yg = np.linspace(min(y), max(y), 300)
    X, Y = np.meshgrid(xg, yg)
    heatmap = griddata((x, y), pf, (X, Y), method='linear')  # Interpolación lineal
    # heatmap = griddata((x, y), q6, (X, Y), method='cubic')  # Interpolación cúbica
    im = ax.imshow(heatmap, extent=(min(x), max(x), min(y), max(y)), origin='lower', cmap='Greens')
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
    ax.set_title(f'Heatmap $\phi$ {n_frame}')


    ax2 =fig.add_subplot(122)
    ax2.set_title(f'KDE $\phi$ {n_frame}')
    ax2.set_xlim([0, 1])
    ax2.set_xlabel(r"$\phi$")
    ax2.set_ylim([0, 8])
    pf_x = np.linspace(0, 1, 400)
    kde_q = gaussian_kde(pf)
    ax2.plot(pf_x, kde_q(pf_x))


    plt.tight_layout()
    plt.savefig(f'pf_{n_png:06d}.png')
    n_png += 1
    plt.close()

