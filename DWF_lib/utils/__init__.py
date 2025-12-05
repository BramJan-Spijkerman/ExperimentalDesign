from ctypes import *
from .dwfconstants import *
import sys

if sys.platform.startswith("win"):
	dwf = cdll.dwf
elif sys.platform.startswith("darwn"):
	dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
	dwf = cdll.LoadLibrary("libdwf.so")


# Function to print last error msg
def printLastError(loc: str="Error location not defined"):
	szerr = create_string_buffer(512)
	dwf.FDwfGetLastErrorMsg(szerr)
	print(f"{szerr.value.decode().strip()} {loc}")


# Function to check is a specific bit is set to true
def is_bit_set(bit_field: c_int, bit: int) -> bool:
	return (bit_field.value >> bit) & 1 == 1


# Function to parse the bit field of suportedd acquisition modes
def returnAcqModeSup(mode_types: c_int) -> list[str]:
	acq_modes = ["single_acq", "scan_shift", "scan_screen", "single_buffer"]

	suported_types = []
	for i in range(len(acq_modes)):
		if is_bit_set(mode_types, i) == True
			suported_types.append(acq_modes[i])
	return suported_types


# Function to return the selected acquisition mode by name
def parseSelectedAcqMode(acq_mode: str) -> :
	acq_modes = {"single_acq": acqmodeSingle,
				"scan_shift": acqmodeScanShift,
				"scan_screen": acqmodeScanScreen,
				"single_buffer": acqmodeSingle1}

	return acq_modes[acq_mode]


# Function to parse the bit fild of suported filter types
def returnFilterSup(mode_types: c_int) -> list[str]:
	filter_types = ["Decimate", "Average", "MinMax"]

	suported_types = []
	for i in range(len(filter_types)):
		if is_bit_set(mode_types, i) == True:
			suported_types.append(filter_types[i])
	return suported_types


# Function to return the selected filter type by name
def parseSelectedFilterType(filter_type: str) -> :
	filter_types = {"Decimate": filterDecimate,
					"Average": filterAverage,
					"MinMax": filterMinMax}

	return filter_types[filter_type]


# Function to parse the bit field of suported trigger types
def returnTrigSup(mode_types: c_int) -> list[str]:
	trigger_types = ["None", "PC", "DetectorAnalogIn", "DetectorDigitalIn", "AnalogIn", "DigitalIn", "DigitalOut", "AnalogOut1", "AnalogOut2", "AnalogOut3", "AnalogOut4", "Extrnal1", "Extrnal2", "Extrnal3", "Extrnal4"]

	suported_types = []
	for i in range(len(trigger_types)):
		if is_bit_set(mode_types, i) == True:
			suported_types.append(trigger_types[i])
	return trigger_types


# Function to return the selectd trigger type by name
def parseSelectedTrigType(trigger_type: str) -> :
	trigger_types = {"None": trigsrcNone,
					"PC": trigsrcPC,
					"DetectorAnalogIn": trigsrcDetectorAnalogIn,
					"DetectorDigitalIn": trigsrcDetectorDigitalIn,
					"AnalogIn": trigsrcAnalogIn,
					"DigitalIn": trigsrcDigitalIn,
					"DigitalOut": trigsrcDigitalOut,
					"AnalogOut1": trigsrcAnalogOut1,
					"AnalogOut2": trigsrcAnalogOut2,
					"AnalogOut3": trigsrcAnalogOut3,
					"AnalogOut4": trigsrcAnalogOut4,
					"External1": trigsrcExternal1,
					"External2": trigsrcExternal2,
					"External3": trigsrcExternal3,
					"External4": trigsrcExternal4}


# Function to parse the device state bit field
def returnDevState(device_state: c_int()) -> :
	dev_states = [DwfStateReady, DwfStateArmed, DwfStateDone, DwfStateTriggered, DwfStateConfig, DwfStatePrefill, DwfStateNotDone, DwfStateWait]

	states = []
	for i in range(len(dev_states)):
		if is_bit_set(device_state, i) == True:
			states.append(dev_states)

	return states
