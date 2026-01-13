import pandas as pd
import numpy as np
from DWF_lib.scope_wrapper import ScopeWrapper
import matplotlib.pyplot as plt
import time
import os

N = 100
buffer_size = 8192
reference_file = "ref_13-01-2026"

# Make sure path exists
data_path = os.path.join(r"C:\Users\Bram_\Documents\GitHub\ExperimentalDesign\data", "reference")
if not os.path.exists(data_path):
	os.mkdir(data_path)

file_path = os.path.join(data_path, reference_file)

Scope = ScopeWrapper(100_000_000, voltage_range=5, buffer_size=buffer_size)

voltage = np.zeros((buffer_size))
for i in range(N):
	voltage += Scope.Acquire()
	
	while Scope.busy:
		time.sleep(0.1)
		
voltage / N
plt.plot(voltage)

np.save(file_path, voltage)

Scope.close()
