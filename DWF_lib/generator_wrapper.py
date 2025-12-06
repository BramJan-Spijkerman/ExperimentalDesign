from .utils import *


class GeneratorWrapper:

	def __init__(self, hdwf: c_int, log: bool=False):
		self.hdwf: c_int = hdwf
		self.log: bool = log

		if self.log == True:
			self.printDeviceCfg()


	# Print the device config
	def printDeviceCfg(self) -> bool:


		error = printLastError("Error in getting device config")
		if error == False:
			print("Printing device config")
		return error
