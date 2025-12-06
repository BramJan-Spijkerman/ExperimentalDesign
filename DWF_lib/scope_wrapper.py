from .utils import *
from numpy import array


class ScopeWrapper:

	def __init__(self, hdwf: c_int, log: bool=False):
		self.hdwf = hdwf
		self.log: bool = log

		self.dev_cfg: dict = {}
		self.chan_cfg: dict = {}

		if self.log == True:
			self.printDeviceCfg()


	# Print out the device configurations
	def printDeviceCfg(self) -> bool:
		# Init variables
		f_min, f_max = c_double(), c_double()
		n_bits = c_int()
		buff_min, buff_max = c_int(), c_int()
		noise_size_max = c_int()
		acq_modes = c_int()

		# Write data to variables
		dwf.FDwfAnalogInFrequencyInfo(self.hdwf, byref(f_min), byref(f_max))
		dwf.FDwfAnalogInBitsInfo(self.hdwf, byref(n_bits))
		dwf.FDwfAnalogInBufferSizeInfo(self.hdwf, byref(buff_min), byref(buff_max))
		dwf.FDwfAnalogInNoiseSizeInfo(self.hdwf, byref(noise_size_max))
		dwf.FDwfAnalofInAcquisitionModeInfo(self.hdwf, byref(acq_modes))

		# Parse acquisition mode types and verify no errors occeured
		suported_acq_modes = returnAcqModeSup(acq_modes)
		error = printLastError("Error in getting device config")
		# Print device config info if no errors where encountered
		if error == False:
			print(f"Device AI info: \nFrequency range: [{f_min.value}, {f_max.value}] \nADC bits: {n_bits.value} \nBuffer size: [{buff_min.value}, {buff_max.value}] \nMax noise buffer size: {noise_size_max.value} \nsuported acq types {suported_acq_modes}")
		return error


	# Set the general device config
	def setDeviceCfg(self, cfg: dict) -> bool:
		# Initialize variables
		self.dev_cfg = cfg
		sample_freq = c_double(cfg["sample_frequency"])
		buffer_size = c_int(cfg["buffer_size"])
		acq_mode = parseSelectedAcqMode(cfg["acquisition_mode"])

		# Set device config from variables
		dwf.FDwfAnalogInFrequencySet(self.hdwf, sample_freq)
		dwf.FDwfAnalogInBufferSizeSet(self.hdwf, buffer_size)
		dwf.FDwfAnalogInAcquisitionModeSet(self.hdwf, acq_mode)

		# Check for errors and return error bool
		return printLastError("Error in setting device config")


	# Print channel configurations
	def printChannelCfg(self) -> bool:
		# Initialize variables
		channel_count = c_int()
		channel_filter = c_int()
		v_min, v_max, v_step = c_double(), c_double(), c_double()
		offset_min, offset_max, offset_step = c_double(), c_double(), c_double()
		attenuation = c_double()
		enable = c_int()

		# Write to general variables
		dwf.FDwfAnalogInChannelCount(self.hdwf, byref(channel_count))
		dwf.FDwfAnalogInFilterInfo(self.hdwf, byref(channel_filter))
		dwf.FDwfAnalogInRangeInfo(self.hdwf, byref(v_min), byref(v_max), byref(v_step))

		# Lists for channel specific variables
		offset_min_lst = []
		offset_max_lst = []
		offset_step_lst = []
		attenuation_lst = []
		enable_lst = []
		# Loop over all channels to fil lists
		for i in range(channel_count.value):
			dwf.FDwfAnalogInChannelOffsetInfo(self.hdwf, c_int(i), byref(offset_min), byref(offset_max), byref(offset_step))
			dwf.FDwfAnalogInAttenuationGet(self.hdwf, c_int(i), byref(attenuation))
			dwf.FDwfAnalogInEnableGet(self.hdwf, c_int(i), byref(enable))

			offset_min_lst.append(offset_min)
			offset_max_lst.append(offset_max)
			offset_step_lst.append(offset_step)
			attenuation_lst.append(attenuation)
			enable_lst.append(enable)

		# Parse filter types suported by channels and check for errors
		filter_types = returnFilterSup(channel_filter)
		error = printLastError("Error occeured in getting channel config info")
		# Print configs if no error was encountered
		if error == False:
			print(f"General channel info: \nChannel count: {channel_count.value} \nSuported filter types: {filter_types} \nRange: [{v_min.value}, {v_max.value}, {v_step.value}]")

			for i in range(channel_count.value):
				print(f"channel: {i} \nOffset: [{offset_min.value}, {offset_max.value}, {offset_step.value}] \nAttenuation: {attenuation_lst[i].value}] \nEnable: {bool(enable_lst[i].value)}")
		return error


	# Set channel config
	def setChannelCfg(self, chan_idx: int, cfg: dict) -> bool:
		self.chan_cfg = cfg
		filter_type = parseSelectedFilterType(cfg["filter_type"])
		Range = c_double(cfg["range"])
		offset = c_double(cfg["offset"])
		attenuation = c_double(cfg["attenuation"])

		dwf.FDwfAnalogInChannelEnableSet(self.hdwf, c_int(chan_idx), c_int(1))
		dwf.FDwfAnalogInChannelFilterSet(self.hdwf, c_int(chan_idx), filter_type)
		dwf.FDwfAnalogInChannelRangeSet(self.hdwf, c_int(chan_idx), Range)
		dwf.FDwfAnalogInChannelOffsetSet(self.hdwf, c_int(chan_idx), offset)
		dwf.FDwfAnalogInChannelAttenuationSet(self.hdwf, c_int(chan_idx), attenuation)

		return printLastError("Error in setting channel config")


	# Print trigger info
	def printTrigInfo(self) -> bool:
		print("Not yet implemented")
		return printLastError("Error in getting trigger info")


	# Get data from measurement
	def Acquire(self) -> Array | bool:
		




		return data, printLastError("Error in retrieving measurement data")




if __name__ == "__main__":
	from device_wrapper import DeviceWrapper

	dev = DeviceWrapper()
	dev_handler = dev.open(-1)

	scope = ScopeWrapper(dev_handler, True)
	scope.printdeviceCfg()

	dev_config = {"": }
	message = scope.setDeviceCfg(dev_config)

	message = scope.printChannelCfg()

	chan_config = {"": }
	message = scope.setChannelCfg(0, chan_config)

	data, message = scope.Acquire()
