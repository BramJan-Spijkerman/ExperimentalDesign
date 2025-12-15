#############################################################################
# Expriment control variables										 	 	#
#############################################################################
sample_rate 		= 100_000_000		# Sample rate of the scope [Hz]  	#
voltage_range 		= 10.0 				# Range of the scope 	   [V]   	#
stage_com_port 		= "COM4" 			# Com port of the stage 		 	#
Kp					= 1 				# Proportional PID-gain 		 	#
Ki 					= 1 				# Integral PID-gain 			 	#
setpoint 			= 0 				# Target point PID 				 	#
thershold 			= 0.2 				# Allowed error in setpoint 	 	#
data_file			= "first_order" 	# File in which to log stage data	#
number_of_cycles	= 4					# Number of cycles in the progam	#
#############################################################################


"""
Code to perform an experiment where the speed of light is measured by
measureing the location of pointswhere the second order correlation
function is zero
"""


#------------FROM HERE DO NOT TOUCH----------------------------------#

# Dependencies
from DWF_lib.scope_wrapper import ScopeWrapper
from stage_controler.my_stage import MyStage
from PID_controler.pid_controler import PIDControler
from analysis.file_loger import Logger
from datetime import datetime
import os


# make file directory and create unique name for file
curent_time = datetime.now()
data_path = os.path.join(r"analysis/data", data_file)
if not os.path.exists(data_path):
	os.mkdir(data_path)


# Create file names
stage_file = os.path.join(data_path, "stage_log", current_time)
scope_file = os.path.join(data_path, "scope_log", current_time)


# Setting up Device controlers 										 
Scope = ScopeWrapper() 												# Scope 		 
Stage = MyStage("stage1", "COM4", stage_file) 						# Delay stage 	 
PIcontroler = PIDControler(Kp, Ki, 0, setpoint) 					# PID-controler  
logger_scope = Logger(scope_file, ["Voltage"])						# File reader/writer for scope
logger_stage = Logger(stage_file, ["target_pos", "current_pos"])	# File reader/writer for stage


# Finds a minimum in the correlation function using PI-controler
def find_minimum(signal: float):
	# Get the current signal
	current_signal = signal

	# Write the signal to file
	logger_scope.write([current_signal])

	# While threshold is not reached converge to setpoint
	while thershold > current_signal:
		# Compute amount to move from current signal
		to_move = PIcontroler.compute(signal, 1)

		# Move stage
		Stage.move(f"+{to_move}")
		# Measure signal
		current_signal = np.mean(Scope.Acquire())
		# Write current signal to file
		logger_scope.write([current_signal])


# For loop to get a number of zeros in 
for i in range(number_of_cycles):
	print("Taking measurement...")
	voltage = np.mean(Scope.Acquire())
	find_minimum(voltage)
	print("Minimum found, proceding to find the next")
	Stage.move("+10")



# Perform prelimenary analysis
scope_data["Voltage"] = logger_scope.read()
stage_data["actual_pos"] = logger_stage.read()

# Plot data
fig = plt.figure(figsize=(9, 5))
ax = fig.add_subplot()
ax.plot(stage_data, scope_data/max(scope_data), label="correlation function")
ax.set_xlabel("Stage position [mm]")
ax.set_ylabel("Normalized signal [-]")
fig.tight_layout()

plt.show()