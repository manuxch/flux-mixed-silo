#!/usr/bin/env python3

import numpy as np
from scipy.spatial import Voronoi, ConvexHull
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

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


fin = open("frm.xy", "r")
data = fin.readlines()
fin.close()

id = []
x = []
y = []
r = []

for linea in data:
    l = linea.split()
    if int(l[0]):
        id.append(int(l[0]))
        x.append(float(l[2]))
        y.append(float(l[3]))
        r.append(float(l[4]))
puntos = np.stack((x,y), axis=1)
print(puntos.shape)
pf = packing_fraction(puntos, r)
# for i, p in enumerate(puntos):
    # print(i, p, pf[i])
# quit()
xg = np.linspace(min(x), max(x), 100)
yg = np.linspace(min(y), max(y), 100)
X, Y = np.meshgrid(xg, yg)
print(puntos.shape, puntos.size, pf.shape)
heatmap = griddata(puntos, pf, (X, Y), method='linear')  # Interpolación lineal
plt.imshow(heatmap, extent=(min(x), max(x), min(y), max(y)), origin='lower', cmap='seismic')
plt.colorbar()  # Agrega una barra de color para mostrar la escala de valores
# plt.scatter(puntos[:, 0], puntos[:, 1], c=pf, cmap='hot', edgecolor='black')  # Muestra los puntos originales
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Mapa de calor')
plt.show()

