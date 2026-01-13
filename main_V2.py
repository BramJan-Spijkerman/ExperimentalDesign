#############################################################################
# Expriment control variables										 	 	#
#############################################################################
sample_rate 		= 100_000_000		# Sample rate of the scope [Hz]  	#
voltage_range 		= 5 				# Range of the scope 	   [V]   	#
stage_com_port 		= "COM4" 			# Com port of the stage 		 	#
data_file			= "measurement" 	# File in which to log stage data	#
delay_step 			= 1 				# Step in optical path delay 	    #
N_cycles  			= 1 				# Number of measurement cycles 	    #
stage_min 			= 1	 				# Minimum delay stage position 	 	#
stage_max 			= 190				# Maximum delay stage position 	  	#
reference			= "ref_13-01-2026.npy"	# Reference intensity measurement	#
scope_buffer_size 	= 8192 				# Buffer size for scope Acquisition #
#############################################################################






# Dependencies
from DWF_lib.scope_wrapper import ScopeWrapper
from stage_controler.my_stage import MyStage
from analysis.file_logger import Logger
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import time
import os


########## Link to files ##########

# make file directory and create unique name for file
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")	# Current time

# Create directories for the data files
data_path = os.path.join(r"C:\Users\Bram_\Documents\GitHub\ExperimentalDesign\data", data_file)
if not os.path.exists(data_path):
	os.mkdir(data_path)


# Create file names
stage_file = data_path + "\stage_log_sweep" + current_time 					# Path to stage data
scope_file = data_path + "\scope_log_sweep" + current_time 					# Path to scope data
reference_file = r"C:\Users\Bram_\Documents\GitHub\ExperimentalDesign\data\reference\ref_13-01-2026.npy"		# Path for reference measurement
stage_logger = Logger(stage_file, ["target_pos [mm]", "actual_pos [mm]"]) 	# Logger for stage file

# Setting up Device controlers
Scope = ScopeWrapper(sample_rate=sample_rate, voltage_range=voltage_range)	# Scope
Stage = MyStage("stage1", "COM4", stage_file) 						 	  	# Delay stage


########## Generate stage positions and empty array from settings ##########

# Generate stage positions from settings
stage_pos = np.arange(stage_min, stage_max, delay_step/2)
number_of_steps = len(stage_pos)
Voltage = np.zeros((N_cycles, len(stage_pos)))


########## Some utility functions ##########

# Function to block the loop until stage has finished moving
def wait_on_stage():
	while Stage.is_moving:
		time.sleep(0.1)

	# Wait for stage to halt
	time.sleep(0.5)


# Function to block the loop until scope has finished aquire
def wait_on_scope():
	while Scope.busy:
		time.sleep(0.1)
		
	time.sleep(0.5)


# Function to plot data
def plot(x, y):
	fig = plt.figure()
	ax = fig.add_subplot()
	ax.plot(x, y)
	ax.set_xlabel("Optical delay [mm]")
	ax.set_ylabel("Voltage [V]")
	ax.grid()
	fig.tight_layout()
	plt.show()
	
	
########## Measurement program starts here ##########
	
# Reset the stage
Stage.reset()
wait_on_stage()


# Main loop
# Loop over cycles
for j in range(N_cycles):

	# Loop over delay steps
	for i in range(len(stage_pos)):

		# Select stage position
		if j%2 == 0:
			step_nr = i
		else:
			step_nr = number_of_steps - i


		# Print info and move stage
		print(f"Cycle: {j+1} / {N_cycles}	Step: {step_nr} / {number_of_steps}")
		Stage.move(f"={stage_pos[step_nr]}")

		wait_on_stage()
		
		Voltage[j, i] = np.mean(Scope.Acquire())

		wait_on_scope()

		plot(stage_pos[:i]*2, np.mean(Voltage[:j+1, :i], axis=0))


# Correct for reference
reference_data = np.mean(np.load(reference_file)) + np.zeros((N_cycles, len(delay_step)))
Voltage -= reference_data

np.save(Voltage, scope_file)