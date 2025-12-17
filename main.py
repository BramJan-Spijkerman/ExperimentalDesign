#############################################################################
# Expriment control variables										 	 	#
#############################################################################
sample_rate 		= 100_000_000		# Sample rate of the scope [Hz]  	#
voltage_range 		= 5 				# Range of the scope 	   [V]   	#
stage_com_port 		= "COM4" 			# Com port of the stage 		 	#
data_file			= "first_order" 	# File in which to log stage data	#
delay_step 			= 1 				# Step in optical path delay 	    #
N_cycles  			= 10 				# Number of measurement cycles 	    #
stage_min 			= 1	 				# Minimum delay stage position 	 	#
stage_max 			= 190				# Maximum delay stage position 	  	#
#############################################################################

"""
Note Always reset stage before doing the thing
"""





# Dependencies
from DWF_lib import ScopeWrapper
from stage_controler import MyStage
from analysis import Logger
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
from datetime import datetime
import time
import os


# make file directory and create unique name for file
current_time = datetime.now().strftime("%d-%H-%M")
data_path = os.path.join(r"C:\Users\Bram_\Documents\GitHub\ExperimentalDesign\data", data_file)
if not os.path.exists(data_path):
	os.mkdir(data_path)


# Create file names
stage_file = data_path + "\stage_log_sweep" + current_time
scope_file = data_path + "\scope_log_sweep" + current_time
# reference_file =  os.path.join(data_path, "regerence_file", "_test", current_time)


# Setting up Device controlers
Scope = ScopeWrapper(voltage_range=voltage_range)					# Scope
Stage = MyStage("stage1", "COM4", stage_file) 						# Delay stage
logger_scope = Logger(scope_file, ["Voltage"])						# File reader/writer for scope
logger_stage = Logger(stage_file, ["target_pos", "current_pos"])	# File reader/writer for stage

stage_pos = np.arange(stage_min, stage_max, delay_step/2)
stage_pos = stage_pos[:-1]
Voltage = np.zeros((len(stage_pos)-1))


# Reset the stage
Stage.reset()
while Stage.is_moving:
	time.sleep(0.1)


# Function to step the delay stage
def step(i: int, move_type: str, j: int):
	if move_type == "-": 
		current_step = len(stage_pos)-1 - i
		i = -1*i
	else:
		current_step = i
	
	# Print info and move stage
	print(f"Cyle: {j} / {N_cycles}    Step: {current_step} / {len(stage_pos)-1}")
	Stage.move(f"={stage_pos[current_step]}")
	
	while Stage.is_moving:
		time.sleep(0.1)
	
	# Wait for stage to halt
	time.sleep(0.5)
	
	Voltage[i] += np.mean(Scope.Acquire())
	while Scope.busy:
		time.sleep(0.1)
		
	# Make ugly graph to look at and keep away boredom
	plt.plot(stage_pos, Voltage/j)
	
	# Write to scope log number, cycle
	#logger_scope.write([@...@])




# Main loop
for j in range(N_cycles):
	if j%2 == 0:
		move_type = "+"
	else:
		move_type = "-"
		
	# Do this for the length of the stage
	for i in range(len(stage_pos)-1):
		step(i, move_type, j)

Voltage /= N_cycles
logger_scope.write([Voltage])

Stage.close()
Scope.close()

# # Preliminary analysis
# # background = np.mean(logger_reference["ref"])
# signal = logger_scope.read()["Voltage"] #- background
# stage_pos = logger_scope.read()["current_pos"]

# y = np.arccos(signal)

# result = linregress(stage_pos*10**(-3), y)
# X = np.linspace(min(stage_pos), max(stage_pos), 10**3)

# fig = plt.figure(figsize=(9, 5))
# ax = fig.add_subplot()
# ax.scatter(stage_pos*10**(-3), y, label="data")
# ax.plot(X, result.slope*X+result.intercept, label="fit")
# ax.set_xlabel("stage position [m]")
# ax.set_ylabel("arccos(U) [V]")

# fig.tight_layout()
# plt.show()
