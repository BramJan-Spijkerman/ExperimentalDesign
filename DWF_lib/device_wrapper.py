from utils import *



class DeviceWrapper:

	def __init__(self, log: bool=False):
		self.log = log

		if self.log == True:
			error = printLastError("Error in starting Device class")

		cDevice = c_int()

		dwf.FDwfEnum(enumfilterAll, byref(cDevice))
		if self.log == True:
			print(f"{cDevice.value} devices detected")


	# Open device at dev_idx
	def open(self, dev_idx: int):
		hdwf = c_int()
		dwf.FDwfDeviceOpen(c_int(dev_idx), byref(hdwf))

		if hdwf.value == hdwfNone.value:
			error = printLastError(f"failed to open device at index {dev_idx}")
			quit()
		else:
			print("Device opened Sucessfully")
			return hdwf


	# Close device at dev_idx
	def close(self, hdwf) -> None:
		dwf.FDwfDeviceClose(hdwf)
		if self.log == True:

			error = printLastError(f"failed to close device")
			if error == True:
				return
			else:
				print("Device closed properly")





if __name__ == "__main__":
	import time

	dev = DeviceWrapper(log=True)
	dev_handler = dev.open(-1)
	time.sleep(2)
	dev.close(dev_handler)
