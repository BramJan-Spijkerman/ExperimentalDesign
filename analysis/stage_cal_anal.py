import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.stats import linregress, anderson
from statsmodels.api import qqplot
import numpy as np
import pandas as pd

# Data
y = np.array([9.4, 11.75, 14.15, 16.75, 19.3, 21.75, 24.3, 26.95, 29.15, 31.9, 34.3, 36.9, 39.45, 41.9, 44.3, 46.8, 49.4, 51.85, 54.4, 56.95, 59.4, 61.85, 64.35, 66.9, 69.35, 71.95, 74.4, 76.85, 79.3, 81.85, 84.4, 86.9, 89.4, 91.9, 94.35, 96.95, 99.4, 101.85, 104.3, 106.95, 109.3, 111.9, 114.35, 116.8, 119.3, 121.75, 124.15, 126.8, 129.3, 131.8, 134.3, 136.85, 139.4, 141.8, 144.25, 146.4, 149.4, 151.9, 154.4])
x = np.linspace(0, len(y)-1, len(y)) * 10**3

# Do regression
result = linregress(x, y)

# Calculate predicted and residuals
X = np.linspace(0, x[-1], 10**4)
Y = result.slope*X + result.intercept
resid = result.slope*x+result.intercept - y

# Do anderson darling test
anderson_result = anderson(resid, "norm")


# Print some statistics
print(f"Slope: {result.slope} ± {result.stderr}\nIntercept: {result.intercept} ± {result.intercept_stderr}\nR^2: {result.rvalue}")
print(f"Mean residuals: {np.mean(resid)}\nStandard deviation residuals: {np.std(resid)}")
print("\n", anderson_result)


# Plot a  summary figure
fig_sumary = plt.figure(figsize=(11, 5))
gs = GridSpec(nrows=2, ncols=5)

ax_fit = fig_sumary.add_subplot(gs[0, :4])
ax_fit.plot(X*10**(-3), Y, label="fit", color="#FFDE59")
ax_fit.scatter(x*10**(-3), y, label="data")
ax_fit.grid()
ax_fit.set_xlabel("10^3 steps made [-]")
ax_fit.set_ylabel("Distance traveled [mm]")
ax_fit.legend()
ax_fit.title.set_text("Fit line")

ax_resid = fig_sumary.add_subplot(gs[1, :2])
ax_resid.plot(x*10**(-3), resid)
ax_resid.grid()
ax_resid.set_xlabel("10^3 steps made [-]")
ax_resid.set_ylabel("Residuals [mm]")
ax_resid.title.set_text("Plot of residuals")

ax_hist = fig_sumary.add_subplot(gs[1,2:4])
ax_hist.hist(resid)
ax_hist.grid()
ax_hist.set_xlabel("Residuals [mm]")
ax_hist.set_ylabel("Count [-]")
ax_hist.title.set_text("Histogram of residuals")

ax_box = fig_sumary.add_subplot(gs[:, 4])
ax_box.boxplot(resid)
ax_box.grid()
ax_box.set_ylabel("Residuals [mm]")
ax_box.title.set_text("Boxplot residuals")

fig_sumary.tight_layout()


# Plot fit line
fig_fit = plt.figure(figsize=(9, 5))
ax = fig_fit.add_subplot()
ax.plot(X*10**(-3), Y, label="fit", color="#FFDE59")
ax.scatter(x*10**(-3), y, label="data")
ax.grid()
ax.set_xlabel("10^3 steps made [-]")
ax.set_ylabel("Distance traveled [mm]")
ax.legend()
fig_fit.tight_layout()


# QQ plot of residuals
fig_QQ = qqplot(resid, line="45")

plt.show()