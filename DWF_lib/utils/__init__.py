from ctypes import *
from .dwfconstants import *
import sys

if sys.platform.startswith("win"):
	dwf = cdll.dwf
elif sys.platform.startswith("darwn"):
	dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
	dwf = cdll.LoadLibrary("libdwf.so")