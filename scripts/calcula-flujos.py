#!/usr/bin/env python3

import argparse
import glob
import numpy as np
import flujo as fl

parser = argparse.ArgumentParser(description="Cálculo de caudal de descarga en archivos de salida.")
parser.add_argument("-o", "--out", help="Nombre del archivo de resultados", required=True)
parser.add_argument("-m", "--mass",
            help="Masa de un grano (gramos) (=1: flujo de partículas). Default: valor experimental",
            type=float, default=0.1319, required=False)
parser.add_argument("-t", "--t_factor",
            help="Escala de tiempo (sim -> exp [s]). Default: valor experimental",
            type=float, default=0.01798809, required=False)
parser.add_argument("-n", "--n_trials",
            help="Número de intentos MC (default: 5000.",
            type=int, default=5000, required=False)
parser.add_argument("-r", "--r2", help="Valor objetivo de R^2 (default: 0.9999.",
            type=float, default=0.9999, required=False)

args = parser.parse_args()
oFile = args.out
m = args.mass
tf = args.t_factor
n_trials = args.n_trials
r2 = args.r2


files = glob.glob("*.dat")
print("Archivos a analizar: ", len(files))

Q = {}
calc_failed = 0
for fname in files:
    f = fname.split("_")
    angle = int(f[1])
    if f[0][-1] == "W":
        angle = 90 - angle
    t, g = np.loadtxt(fname, usecols=(2, 4), unpack=True)
    res = fl.flujo_masico(t, g, m, tf, False, n_trials, r2)
    if res:
        print(f"A: {angle}, caudal: ({res['caudal']:.3f} ± {res['cov_caudal']:.3f}) g")
        if angle in Q:
            Q[angle].append(res['caudal'])
        else:
            Q[angle] = [res['caudal']]
    else:
        print("No se puede calcular el flujo para " + fname)
        calc_failed += 1

print(f"No se pudo calcular el flujo en {calc_failed} casos ({calc_failed/len(files) * 100:.2f}%)")

fout = open(oFile, "w")
fout.write("# Ángulo_deg Flujo_1 ... Flujo_n\n")
for a in sorted(Q.keys()):
    s = str(a)
    for f in Q[a]:
        s += " " + str(f)
    fout.write(str(s) + "\n")
