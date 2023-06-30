#!/usr/bin/env python3

import numpy as np

rho =1.0 / (np.pi * 0.5**2)
print(rho)

def r_s(s):
    return np.sqrt(s / (rho * np.pi))

chg = np.linspace(0, 50, 20)
# print(chg)

sU = [(1.0 + c/100.0) for c in chg]
sL = [(1.0 - c/100.0) for c in chg]

# print(sU)
# print(sL)

# for c, u, l in zip(chg, sU, sL):
    # print(c, u, l, u/l)


asu = np.array(sU)
asl = np.array(sL)

ru = r_s(asu)
rl = r_s(asl)

# for c, u, l in zip(chg, ru, rl):
    # print(c, u, l, u/l)
print(chg)
print(ru)
print(rl)
