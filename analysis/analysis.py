import pandas as pd
import os
import matplotlib.pyplot as plt
from scipy.stats import linregress, anderson
from statsmodels.api import qqplot
import numpy as np

# Path to data folder
path = r"PATH TO FILES"

# Make sure path exists, else make it


# Make paths to stage position file and frequency data file
stage_dat_path = os.path.join(path, "stage")
freq_dat_path = os.path.join(path, "freq")


# Make length differences and number
stage_data = pd.read_csv(stage_dat_path)
stage_position = stage_data["stage_pos"].to_numpy()
length_diferences = stage_position - stage_position[0]
m = np.arange(len(stage_position))

# Get frequency data
freq_data = pd.read_csv(freq_dat_path)
f_M = freq_data["f_M"]

# Calculate the x variable
x = m / (2*f_M)


# Do regression
result = linregress(x, length_diferences)
X = np.linspace(0, len(stage_position), 10**3)
Y = result.slope * X + result.intercept


fig = plt.figure(figsize=(9, 5))
ax = fig.add_subplot()

ax.plot(X, Y, label="fit", color="r")
ax.scatter(x, length_diferences, label="data")
ax.grid()

ax.set_xlabel("m/2f_M [s]")
ax.set_ylabel("L_i-L_0 [m]")

fig.tight_layout()


residuals = length_diferences - (result.slope * x + result.intercept)
fig = qqplot(residuals, line="45")

plt.show()
