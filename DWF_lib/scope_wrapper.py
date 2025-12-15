from utils import *
import numpy as np
from scipy.signal import butter, filtfilt

class ScopeWrapper:

	def __init__(self, sample_rate: float=100_000_000, buffer_size: int=8192, channel: int=0, voltage_range: float=10.0):
		self.hdwf = c_int()
		self.channel = channel
		self.sample_rate = sample_rate
		self.buffer_size = buffer_size
		self.voltage_range = voltage_range

		self.nyq = self.sample_rate / 2

		# Open device
		dwf.FDwfDeviceOpen(c_int(-1),  byref(self.hdwf))

		if self.hdwf.value == 0:
			err = create_string_buffer(512)
			dwf.FDwfGetLastErrorMsg(err)
			raise RuntimeError("Failed to open device: "  + err.value.decode())

		# Analog in config
		dwf.FDwfAnalogInFrequencySet(self.hdwf, c_double(self.sample_rate))
		dwf.FDwfAnalogInBufferSizeSet(self.hdwf, c_int(self.buffer_size))
		dwf.FDwfAnalogInAcquisitionModeSet(self.hdwf, acqmodeSingle1)

		dwf.FDwfAnalogInChannelEnableSet(self.hdwf, c_int(self.channel), c_bool(True))
		dwf.FDwfAnalogInChannelRangeSet(self.hdwf, c_int(self.channel), c_double(self.voltage_range))

		# Set trigger
		self.trigger_cfg()


	# Config for the trigger
	def trigger_cfg(self, level: float=0.0, hysteresis: float=0.02, edge_rising: bool=True, auto_timeout_s: float=10.0):

		dwf.FDwfAnalogInTriggerSourceSet(self.hdwf, trigsrcDetectorAnalogIn)
		dwf.FDwfAnalogInTriggerChannelSet(self.hdwf, c_int(self.channel))
		dwf.FDwfAnalogInTriggerLevelSet(self.hdwf, c_double(level))
		dwf.FDwfAnalogInTriggerHysteresisSet(self.hdwf, c_double(hysteresis))

		slope = DwfTriggerSlopeRise if edge_rising else DwfTriggerSlopeFall
		dwf.FDwfAnalogInTriggerConditionSet(self.hdwf, slope)
		dwf.FDwfAnalogInTriggerFilterSet(self.hdwf, c_int(0))

		dwf.FDwfAnalogInTriggerAutoTimeoutSet(self.hdwf, c_double(auto_timeout_s))


	def Acquire(self):
		sts = c_byte()

		# Arm scope
		dwf.FDwfAnalogInConfigure(self.hdwf, c_bool(False), c_bool(True))

		# Wait until ready
		while True:
			dwf.FDwfAnalogInStatus(self.hdwf, c_bool(True), byref(sts))
			if sts.value == DwfStateDone.value:
				break

		n = self.buffer_size # <= To read whole buffer
		if n <= 0:
			return np.array([])

		# Read samples
		buf = (c_double * n)()
		dwf.FDwfAnalogInStatusData(self.hdwf, c_int(self.channel), buf, c_int(n))

		return np.frombuffer(buf, dtype=np.float64)


	def close(self):
		dwf.FDwfDeviceClose(self.hdwf)


	def __del__(self):
		try:
			self.close()
		except:
			pass



if __name__ == "__main__":
    Scope = ScopeWrapper()
    data = Scope.Acquire()
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
