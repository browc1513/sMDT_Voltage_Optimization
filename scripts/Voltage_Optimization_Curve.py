import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Load the updated signal area data (make sure it's already been regenerated with the new voltage levels!)
file_path = r"C:\Users\colin\OneDrive\Desktop\Voltage Optimization Data\sMDT_Signal_Area_By_Voltage.csv"
data = pd.read_csv(file_path)

# Group and calculate stats
summary = data.groupby("Voltage (V)")["Signal Area (V·s)"].agg(["mean", "sem"]).reset_index()

# Exponential fit function
def exponential(x, a, b):
    return a * np.exp(b * x)

# Prepare data
voltage_list = np.array(summary["Voltage (V)"])
area_list = np.array(summary["mean"])

# Fit curve
try:
    popt, _ = curve_fit(exponential, voltage_list, area_list, p0=(1e-9, 1e-3), maxfev=10000)
except RuntimeError as e:
    print("Fit failed:", e)
    popt = [np.nan, np.nan]

# Plot
plt.figure(figsize=(10, 6))
plt.errorbar(voltage_list, area_list, yerr=summary["sem"], fmt='o', label="Mean ± Standard Error", color="blue", capsize=4)

# Plot exponential fit
if not np.isnan(popt).any():
    voltage_fit = np.linspace(min(voltage_list), max(voltage_list), 1000)
    area_fit = exponential(voltage_fit, *popt)
    plt.plot(voltage_fit, area_fit, color="red", label=f"Exponential Fit:\n$y = {popt[0]:.2e} \\, e^{{{popt[1]:.2e}x}}$")

# Final touches
plt.title("Voltage Optimization Curve")
plt.xlabel("High-Voltage Supply (V)")
plt.ylabel("Signal Area (V·s)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("Voltage_Optimization_Curve.png", dpi=300)
plt.show()
