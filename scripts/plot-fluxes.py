#!/usr/bin/python3
import argparse
import numpy as np
import matplotlib.pyplot as plt
import flujo

parser = argparse.ArgumentParser(description='Programa para comparar flujos.action=')
parser.add_argument('-s','--sim', help='Simulation file', required=True, action="store")
parser.add_argument('-e','--exp', help='Experimental file', required=True, action="store")

args = parser.parse_args()
insf = args.sim
inef = args.exp

#  te, me = np.loadtxt(inef, delimiter=',', skiprows=1, unpack=True)
te1, me1 = np.loadtxt("../datos-exp/06-21-22_G_deg000_t01.txt", delimiter=',', skiprows=1, unpack=True)
te2, me2 = np.loadtxt("../datos-exp/06-21-22_G_deg000_t02.txt", delimiter=',', skiprows=1, unpack=True)
te3, me3 = np.loadtxt("../datos-exp/06-21-22_G_deg000_t03.txt", delimiter=',', skiprows=1, unpack=True)
te4, me4 = np.loadtxt("../datos-exp/07-07-22_C_deg000_t01.txt", delimiter=',', skiprows=1, unpack=True)
te5, me5 = np.loadtxt("../datos-exp/07-07-22_C_deg000_t02.txt", delimiter=',', skiprows=1, unpack=True)
te6, me6 = np.loadtxt("../datos-exp/07-07-22_C_deg000_t03.txt", delimiter=',', skiprows=1, unpack=True)
ts, ms = np.loadtxt(insf, usecols=(2,4), unpack=True)

mg = 0.1319  # masa de un grano (gr)
t_factor = 0.01798809 # sim > exp

ts *= t_factor
ts += 1.8
ms *= mg
#  me -= 3062
#  mask = te > 1.8

#  plt.plot(te[mask], me[mask], label="Experimental")
plt.plot(te1, me1, label="Exp-01")
plt.plot(te2, me2, label="Exp-02")
plt.plot(te3, me3, label="Exp-03")
plt.plot(te4, me4, label="Exp-04")
plt.plot(te5, me5, label="Exp-05")
plt.plot(te6, me6, label="Exp-06")
plt.plot(ts, ms, label="Simulation")

plt.xlabel("Time (s)")
plt.ylabel("Mass (g)")
plt.legend()
plt.show()

