from file_logger import Logger
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


########## Path to data files ##########

stage_file = r"C:\Users\Bram_\Documents\GitHub\ExperimentalDesign\data\measurement\stage_log_sweep2026-01-13_17-10-21"
scope_file = r"C:\Users\Bram_\Documents\GitHub\ExperimentalDesign\data\measurement\scope_log_sweep2026-01-13_17-10-21"

########################################


# Connect to files
stage_log = pd.read_csv(stage_file)	# File reader/writer for stage

# Get measurement data
optical_delay = stage_log["actual_pos [mm]"].to_numpy() * 2
voltage = np.load(scope_file + ".npy")


def plot(x, y, xlabel, ylabel):
	fig = plt.figure(figsize=(9, 5))
	ax = fig.add_subplot()
	y -= np.mean(y)
	ax.plot(x, y)
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	ax.set_xlim(100, 300)
	ax.grid()

	fig.tight_layout()
	plt.show()


def plot_interference():
	# Plot interference pattern
	plot(optical_delay, voltage, "Optical delay [mm]", "Voltage [V]")


def plot_arccos():
	# Plot phase
	plot(optical_delay, np.arccos(voltage), "Optical delay [mm]", "arccos(V)")


import numpy as np
from scipy.optimize import curve_fit

def cosine_model(t, A, omega, phi):
	return A * np.cos(omega * t + phi)

def fit_cosine(t, y):
	"""
    Fit y(t) = A * cos(omega * t + phi)

    Parameters
    ----------
    t : array-like
        Independent variable (time)
    y : array-like
        Measured data

    Returns
    -------
    params : dict
		Best-fit parameters: A, omega, phi
	errors : dict
		1-sigma uncertainties on parameters
	"""

	t = np.asarray(t)
	y = np.asarray(y)

	# Initial guesses
	A0 = 0.5 * (np.max(y) - np.min(y))

	# Estimate omega from FFT peak
	dt = np.mean(np.diff(t))
	freqs = np.fft.rfftfreq(len(t), dt)
	fft_mag = np.abs(np.fft.rfft(y - np.mean(y)))
	omega0 =  0.020106192982974676 # 2 * np.pi * freqs[np.argmax(fft_mag[1:]) + 1]

	phi0 = 0.0

	p0 = [A0, omega0, phi0]

	popt, pcov = curve_fit(cosine_model, t, y, p0=p0)

	perr = np.sqrt(np.diag(pcov))

	params = dict(A=popt[0], omega=popt[1], phi=popt[2])
	errors = dict(A=perr[0], omega=perr[1], phi=perr[2])
	
	fig = plt.figure(figsize=(9, 5))
	ax = fig.add_subplot()
	y -= np.mean(y)
	ax.plot(t, y)
	ax.plot(t, cosine_model(t, params["A"], params["omega"], params["phi"]), label="fit")
	ax.set_xlabel("Optical delay [mm]")
	ax.set_ylabel("Voltage [V]")
# 	ax.set_xlim(100, 300)
	ax.grid()
	ax.legend()

	fig.tight_layout()
	plt.show()


	return params, errors
