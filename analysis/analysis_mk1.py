import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from numpy.fft import fft, fftfreq
from filer_logger import Logger
import numpy as np
import sys


def moving_average(data, window_size):
	window = np.ones(window_size) / window_size
	return np.convolve(data, window, mode="same")


if sys.platform.startswith("win"):
	stage_file = r"C:\Users\Bram_\Documents\GitHub\ExperimentalDesign\data\first_order\stage_log_sweep16-16-40.csv"
	scope_file = r"C:\Users\Bram_\Documents\GitHub\ExperimentalDesign\data\first_order\scope_log_test16-16-40.csv"
else:
	stage_file = r"/home/brm/pythonWorkspace/UU/interferometerExperiment/data/first_order/stage_log_sweep16-16-40.csv"
	scope_file = r"/home/brm/pythonWorkspace/UU/interferometerExperiment/data/first_order/scope_log_test16-16-40.csv"

stage_log = Logger(stage_file, ["target_pos [mm]", "actual_pos [mm]"])
scope_log = Logger(scope_file, ["Voltage"])

stage_positions = stage_log.read()
scope_signal = scope_log.read()

optical_delay = stage_positions["actual_pos [mm]"] * 2
signal = scope_signal["Voltage"]

L = max(optical_delay) - min(optical_delay)
N_k = len(optical_delay)
k = np.linspace(-np.pi / np.mean(np.diff(optical_delay)),
				np.pi / np.mean(np.diff(optical_delay)),
				N_k)

def optical_dft(delay, V, k):
	w = np.zeros_like(delay)
	w[1:-1] = 0.5 * (delay[2:] - delay[:-2])
	w[0] = 0.5 * (delay[1] - delay[0])
	w[-1] = 0.5 * (delay[-1] - delay[-2])
	
	phase = np.exp(-1j * np.outer(k, delay))
	return phase @ (V * w)


fig = plt.figure(figsize=(9, 10))
gs = GridSpec(nrows=2, ncols=1)
ax = fig.add_subplot(gs[0, 0])
ax.scatter(optical_delay, signal, label="raw data")
ax.plot(optical_delay, moving_average(signal, 5), label="5 point mov mean", color="r")
ax.grid()
ax.set_xlabel("Optical delay [mm]")
ax.set_ylabel("Signal strength [V]")
ax.legend()
ax.title.set_text("raw data")

N = len(signal)
FFT = fft(signal)
FFT_amp = 1/N * abs(FFT[:N//2])
freq = fftfreq(N, 1.9995026315789473*10**(-3))[:N//2]

DFT_amp = abs(optical_dft(optical_delay, signal, k))

ax_fft = fig.add_subplot(gs[1, 0])
# ax_fft.plot(k, DFT_amp, label="DFT")
ax_fft.plot(freq, FFT_amp, label="FFT")
ax_fft.set_xlabel("reciplocal milli metres [1/mm]")
ax_fft.set_ylabel("Amplitude [V]")
ax_fft.set_xlim(0)
ax_fft.legend()
ax_fft.grid()
ax_fft.title.set_text("Fourier transform")

fig.tight_layout()


fig = plt.figure(figsize=(9, 5))
ax = fig.add_subplot()
ax.plot(optical_delay, np.arccos(signal))
ax.set_xlabel("Optical delay [mm]")
ax.set_ylabel("arccos(signal) [V]")
ax.grid()
ax.title.set_text("Arccos(signal)")
fig.tight_layout()



