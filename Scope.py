# -*- coding: utf-8 -*-
"""
Created on Mon Jan 12 11:27:02 2026

@author: Bram_
"""
from DWF_lib.scope_wrapper import ScopeWrapper
import numpy as np

Scope = ScopeWrapper(voltage_range=5)
import time
data = np.zeros((8192))
# 	for i in range(100):
# 		data += Scope.Acquire()
# 		time.sleep(1)
data = Scope.Acquire()
	
data /= 100
		
time = np.arange(0, len(data))*10**6/Scope.sample_rate
Scope.close()

N = len(data)
print(f"data points: {len(data)}")

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from numpy.fft import fft, fftfreq

FFT = fft(data)
FFT_amplitude = 1/N * abs(FFT[:N//2])
freq = fftfreq(N, 1/Scope.sample_rate)*10**(-6)

print(f"Mean of signal: {np.mean(data)}")
print(f"Amplitude at 0 frequncy: {FFT_amplitude[0]}")
fig = plt.figure(figsize=(10, 9))
gs = GridSpec(nrows=2, ncols=1)
ax_time = fig.add_subplot(gs[0, 0])
ax_time.plot(time, data, label="Time signal")
ax_time.set_xlabel("Time [µs]")
ax_time.set_ylabel("Voltage [V]")
ax_time.grid()

ax_freq = fig.add_subplot(gs[1, 0])
ax_freq.plot(freq[:N//2], FFT_amplitude, label="Frequency signal")
ax_freq.set_xlabel("Frequency [MHz]")
ax_freq.set_ylabel("Amplitude [V]")
ax_freq.grid()

fig.tight_layout()
plt.show()