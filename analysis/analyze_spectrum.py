# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 16:15:43 2026

@author: Bram_
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# =========================
# User configuration
# =========================
CSV_FILE = r"C:\Users\Bram_\Documents\GitHub\ExperimentalDesign\data\spectra\moulation_spectrum_13-01-2026_960MHz.DAT"     # input file
X_COL = "Values"                   # frequency / wavelength column name
Y_COL = "501"                   # intensity column name

X_MIN = 960                 # lower bound of peak region
X_MAX = 961                 # upper bound of peak region

# =========================
# Peak models
# =========================
def gaussian(x, A, mu, sigma, c):
    return A * np.exp(-(x - mu)**2 / (2 * sigma**2)) + c

def lorentzian(x, A, mu, gamma, c):
    return A * gamma**2 / ((x - mu)**2 + gamma**2) + c

# =========================
# Load data (handles decimal comma)
# =========================
df = pd.read_csv(CSV_FILE, sep=";", engine="python", header=27, decimal=",")

x = df[X_COL].to_numpy()*1e-6
y = df[Y_COL].to_numpy()

# =========================
# Isolate peak region
# =========================
mask = (x >= X_MIN) & (x <= X_MAX)
x_peak = x[mask]
y_peak = y[mask]

# =========================
# Initial guesses
# =========================
A0 = y_peak.max() - y_peak.min()
mu0 = x_peak[np.argmax(y_peak)]
width0 = (X_MAX - X_MIN) / 10
c0 = y_peak.min()

# =========================
# Gaussian fit
# =========================
popt_g, pcov_g = curve_fit(
    gaussian,
    x_peak,
    y_peak,
    p0=[A0, mu0, width0, c0]
)

perr_g = np.sqrt(np.diag(pcov_g))

# =========================
# Lorentzian fit
# =========================
popt_l, pcov_l = curve_fit(
    lorentzian,
    x_peak,
    y_peak,
    p0=[A0, mu0, width0, c0]
)

perr_l = np.sqrt(np.diag(pcov_l))

# =========================
# Find FWHM
# =========================


# =========================
# Print results
# =========================
print("Gaussian fit:")
print(f"  A     = {popt_g[0]:.6g} ± {perr_g[0]:.3g}")
print(f"  mu    = {popt_g[1]:.6g} ± {perr_g[1]:.3g}")
print(f"  sigma = {popt_g[2]:.6g} ± {perr_g[2]:.3g}")
print(f"  c     = {popt_g[3]:.6g} ± {perr_g[3]:.3g}")

print("\nLorentzian fit:")
print(f"  A     = {popt_l[0]:.6g} ± {perr_l[0]:.3g}")
print(f"  mu    = {popt_l[1]:.6g} ± {perr_l[1]:.3g}")
print(f"  gamma = {popt_l[2]:.6g} ± {perr_l[2]:.3g}")
print(f"  c     = {popt_l[3]:.6g} ± {perr_l[3]:.3g}")

# =========================
# Plot
# =========================
fig = plt.figure()
ax = fig.add_subplot()
ax.plot(x, y, label="Data", alpha=0.6)
ax.plot(x_peak, gaussian(x_peak, *popt_g), label="Gaussian fit")
# ax.plot(x_peak, lorentzian(x_peak, *popt_l), label="Lorentzian fit")
# ax.axvspan(X_MIN, X_MAX, color="gray", alpha=0.15, label="Fit region")
ax.vlines(popt_g[1] - popt_g[2]*np.sqrt(2)*np.log(2), -30, -90, color="m")
ax.vlines(popt_g[1] + popt_g[2]*np.sqrt(2)*np.log(2), -30, -90, color="m")
ax.grid()
ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(-90, -30)
ax.set_xlabel("Frequency [MHz]")
ax.set_ylabel("Amplitude [dB]")
ax.legend()
fig.tight_layout()
plt.show()
