import numpy as np
from numpy.typing import NDArray
from numpy import array
from typing import Any
import csv
import os


# Class to read and write to a file
class Logger:

	# Initialize file name and create file
	def __init__(self, target_file: str, column_names: list[Any]):
		self.target_file = target_file
		self.column_names = column_names
		self._create_file(column_names)


	# Read contents of file
	def read(self) -> dict{str: NDArray}:
		rows = []
		with open(self.target_file, "r", newline="") as file:
			reader = csv.reader(file)
			next(reader, None)
			for row in reader:
				if len(row) >= 1:
					rows.append([float(element) for element in row])

		N_rows = len(rows)
		N_cols = len(rows[0])

		array = np.zeros((N_rows, N_cols))
		for i in range(N_rows):
			for j in range(N_cols):
				array[i, j] = rows[i][j]

		DICT = {}
		for i in range(N_cols):
			DICT[self.column_names[i]] = array[:, i]

		return DICT


	def write(self, values: list[Any]) -> None:
		with open(self.target_file, "r+", newline="") as file:
			file.seek(0, 2)
			writer = csv.writer(file)
			writer.writerow(values)


	def _create_file(self, column_names: list[str]) -> None:
		if not os.path.exists(self.target_file):
			with open(self.target_file, "a", newline="") as file:
				writer = csv.writer(file)
				writer.writerow(column_names)




if __name__ == "__main__":

	logger = Logger(r"date_test.csv", ["Hello", "World"])

	logger.write([1, 2])
	logger.write([3, 4])

	arr = logger.read()
	print(arr)

