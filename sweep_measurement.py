#############################################################################
# Expriment control variables										 	 	#
#############################################################################
sample_rate 		= 100_000_000		# Sample rate of the scope [Hz]  	#
voltage_range 		= 10.0 				# Range of the scope 	   [V]   	#
stage_com_port 		= "COM4" 			# Com port of the stage 		 	#
data_file			= "first_order" 	# File in which to log stage data	#
#############################################################################







# Dependencies
from DWF_lib.scope_wrapper import ScopeWrapper
from stage_controler.my_stage import MyStage
from analysis.filer_logger import Logger
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
from datetime import datetime
import os


# make file directory and create unique name for file
current_time = datetime.now().strftime("%d-%H-%M")
data_path = os.path.join(r"analysis/data", data_file)
if not os.path.exists(data_path):
	os.mkdir(data_path)


# Create file names
stage_file = os.path.join(data_path, "stage_log", "_sweep", current_time)
scope_file = os.path.join(data_path, "scope_log", "_sweep", current_time)


# Setting up Device controlers
Scope = ScopeWrapper() 												# Scope
Stage = MyStage("stage1", "COM4", stage_file) 						# Delay stage
logger_scope = Logger(scope_file, ["Voltage"])						# File reader/writer for scope
logger_stage = Logger(stage_file, ["target_pos", "current_pos"])	# File reader/writer for stage


# Draw updateble plot
fig = plt.figure(figsize=(9, 5))
ax = fig.add_subplot()
line, = ax.plot([], [])
ax.set_xlabel("step [-]")
ax.set_ylabel("Siganl [V]")
fig.tight_layout()
plt.show()

x = []
y = []
# Function to set aproximately 1 step
def step(i: int):
	voltage = np.mean(Scope.Acquire())
	logger_scope.write([voltage])
	Stage.move("+1/400")

	x.append(i)
	y.append(voltage)
	line.set_data(x, y)
	ax.relim()
	ax.autoscale_view()
	plt.draw()



# Do this for the length of the stage
for i in range(84000):
	step(i)


# Preliminary analysis
signal = logger_scope.read()["voltage"]
stage_pos = logger_scope.read()["current_pos"]

y = np.arccos(signal)

result = linregress(stage_pos*10**(-3), y)
X = np.linspace(min(stage_pos), max(stage_pos), 10**3)

fig = plt.figure(figsize=(9, 5))
ax = fig.add_subplot()
ax.scatter(stage_pos*10**(-3), y, label="data")
ax.plot(X, result.slope*X+result.intercept, label="fit")
ax.set_xlabel("stage position [m]")
ax.set_ylabel("arccos(U) [V]")

fig.tight_layout()
plt.show()
