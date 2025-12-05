from .utils import *


class ScopeWrapper:

	def __init__(self, hdwf: c_int, log: bool=False):
		self.hdwf = hdwf
		self.log = log


