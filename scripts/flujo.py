#!/usr/bin/python3
import numpy as np
import argparse
from scipy.stats import linregress
import scipy.stats as sps
import sys
import matplotlib.pyplot as plt


def flujo_masico(t, g, m, tf, plot, n_trials, r2):
    """Calcula el flujo másico de descarga de silo
    Params:
    -------
    t: array con el tiempo de salida del grano
    g: granos descargados en el tiempo t
    m: masa de los granos. Si m = 1, flujo másico = flujo partículas
    tf: factor de conversión de unidades de simulación a experimentales
    plot: si es True hace un gráfico del ajuste
    n_trials: número de intentos de MC
    r2: valor objetivo de R^2

    Return:
    -------
    res: diccionario con los siguientes ítems
        caudal: caudal de descarga en g en el rágimen lineal
        cov_caudal: covarianza del ajuste del caudal
        r2: valor de R**2
        izq: (t, masa) del límite izquierdo del ajuste
        der: (t, masa) del límite derecho del ajuste
        n_fit: cantidad de valores usado en el ajuste
    """
    g *= m
    t *= tf
    g_max_fit = g.max() * 0.85
    g_min_fit = g.max() * 0.05
    dif_min = np.absolute(g-g_min_fit)
    idx_min = dif_min.argmin()
    dif_max = np.absolute(g-g_max_fit)
    idx_max = dif_max.argmin()
    res = {'n_fit': 0, 'caudal': -1}
    mc_trial = 0
    while mc_trial < n_trials:
        lim = np.sort(np.random.randint(idx_min, idx_max, size=2))
        n_points = lim[1] - lim[0]
        if n_points < t.size * 0.3:
            continue
        m, i, r, pv, mstd = linregress(t[lim[0]:lim[1]], g[lim[0]:lim[1]])
        if r**2 > r2:
            if n_points > res['n_fit']:
                res["caudal"] = m
                res["cov_caudal"] = mstd
                res["r2"] = r**2
                res["izq"] = (t[lim[0]], g[lim[0]])
                res["der"] = (t[lim[1]], g[lim[1]])
                res["n_fit"] = g[lim[0]:lim[1]].size
        mc_trial += 1
    if plot:
        plt.plot(t, g, label='mass_out')
        delta_t = t[lim[1]] - t[lim[0]]
        t_fit = np.linspace(t[lim[0]] - 0.5 * delta_t, t[lim[1]] + 0.5 * delta_t, 50)
        plt.plot(t[lim[0]:lim[1]], g[lim[0]:lim[1]], '.', label='mass_fit')
        plt.plot(t_fit, m * t_fit + i, label='fit')
        plt.scatter([t[lim[0]], t[lim[-1]]], [g[lim[0]], g[lim[1]]])
        plt.legend()
        plt.xlabel("t [s]")
        plt.ylabel("t [g]")
        plt.show()

    if (res['caudal'] < 0 or n_points < 10):
        return None
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cálculo de caudal de descarga.")
    parser.add_argument("-f", "--flux", help="Archivo de entrada", required=True)
    parser.add_argument("-m", "--mass",
                        help="Masa de un grano (gramos) (=1: flujo de partículas). Default: valor experimental",
                        type=float, default=0.1319, required=False)
    parser.add_argument("-t", "--t_factor",
                        help="Escala de tiempo (sim -> exp [s]). Default: valor experimental",
                        type=float, default=0.01798809, required=False)
    parser.add_argument("-p", "--plot", help="Muestra un gráfico del ajuste.",
                        type=bool, default=False, required=False)
    parser.add_argument("-n", "--n_trials",
                        help="Número de intentos MC (default: 5000).",
                        type=int, default=5000, required=False)
    parser.add_argument("-r", "--r2", help="Valor objetivo de R^2 (default: 0.9999).",
                        type=float, default=0.9999, required=False)
    parser.add_argument("-g", "--g_type", help="Tipo de grano (1, 2, ...) (Default 0 = total).",
                        type=int, default=0, required=False)

    args = parser.parse_args()
    fin = args.flux
    m = args.mass
    tf = args.t_factor
    plot = args.plot
    n_trials = args.n_trials
    r2 = args.r2
    if args.g_type:
        g_col = 2 + args.g_type
    else:
        g_col = 0
    t, g = np.loadtxt(fin, usecols=(2, g_col), unpack=True)
    res = flujo_masico(t, g, m, tf, plot, n_trials, r2)
    tinv = lambda p, df: abs(sps.t.ppf(p/2, df))
    ts = tinv(0.01, len(t)-2)  # Intervalo de confianza del 98%
    if res:
        print(f"Caudal: ({res['caudal']:.3f} ± {ts * res['cov_caudal']:.3f}) g/s")
        print(f"r_0^2: {res['r2']:.6f}")
        print(f"Ajuste izquierdo: [{res['izq'][0]:.3f}, {res['izq'][1]:.3f}]")
        print(f"Ajuste derecho: [{res['der'][0]:.3f}, {res['der'][1]:.3f}]")
        print(f"Número de puntos de ajuste: {res['n_fit']}")
    else:
        print("No se pudo hallar el caudal.")
