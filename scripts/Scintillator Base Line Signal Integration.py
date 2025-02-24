import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simpson
import os

# Define the directory path (updated for GitHub directory structure)
directory = os.path.join(os.getcwd(), "raw_data", "Experiment_1_Raw_Data")
print(f"Processing files in: {directory}")
print("Files in directory:", os.listdir(directory))

# Define the specific file path (updated to reflect correct file name)
file_name = "sMDT_3400V_Event_001.csv"
file_path = os.path.join(directory, file_name)

# Load Data
df = pd.read_csv(file_path, skiprows=17)
df.columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']

# Extract relevant columns
df = df[['D', 'E', 'K']]  # Time, CH1, CH2
df.columns = ["Time (s)", "CH1 (V)", "CH2 (V)"]
df.dropna(inplace=True)

# Convert columns to numeric
df["Time (s)"] = pd.to_numeric(df["Time (s)"])
df["CH1 (V)"] = pd.to_numeric(df["CH1 (V)"])
df["CH2 (V)"] = pd.to_numeric(df["CH2 (V)"])

# Identify First Hit (Threshold-Based)
threshold = 2.0  # Set based on expected values
first_hit_index = df[(df["CH1 (V)"] > threshold)].index[0]
first_hit_time = df.loc[first_hit_index, "Time (s)"]

# Expected and Detected Timing Difference
expected_hit_time = -4.5e-07  # From oscilloscope settings
time_difference = abs(expected_hit_time - first_hit_time)

# Extract Peak Window (From first hit to return to baseline)
baseline_threshold = 0.5  # Define lower threshold
peak_end_index = df[(df.index > first_hit_index) & (df["CH1 (V)"] < baseline_threshold)].index[0]
peak_duration = df.loc[peak_end_index, "Time (s)"] - first_hit_time

# Integration (Area Under the Curve)
time_window = df.loc[first_hit_index:peak_end_index, "Time (s)"]
ch1_window = df.loc[first_hit_index:peak_end_index, "CH1 (V)"]
ch2_window = df.loc[first_hit_index:peak_end_index, "CH2 (V)"]

ch1_integral = simpson(ch1_window, time_window)
ch2_integral = simpson(ch2_window, time_window)
total_integral = ch1_integral + ch2_integral

# Print Timing and Integral Info
timing_results = pd.DataFrame({
    "Expected Hit Time (s)": [expected_hit_time],
    "Detected Hit Time (s)": [first_hit_time],
    "Time Difference (s)": [time_difference],
    "Start Time (s)": [first_hit_time],
    "End Time (s)": [df.loc[peak_end_index, "Time (s)"]],
    "Peak Duration (s)": [peak_duration],
    "CH1 Integral (V*s)": [ch1_integral],
    "CH2 Integral (V*s)": [ch2_integral],
    "Total Integral (V*s)": [total_integral]
})
print(timing_results)

# Generate Bar Graph (Similar to Reference)
event_numbers = np.arange(1, len(time_window) + 1)

plt.figure(figsize=(14, 7))
plt.bar(event_numbers, ch1_window, color='blue', alpha=0.7, label='CH1 Signal Area')
plt.bar(event_numbers, ch2_window, color='purple', alpha=0.7, label='CH2 Signal Area')

mean_integral = total_integral / len(time_window)
plt.axhline(y=mean_integral, color='red', linestyle='--', label=f'Overall Mean: {mean_integral:.2e}')
plt.fill_between(event_numbers, mean_integral - 0.1 * mean_integral, mean_integral + 0.1 * mean_integral, 
                 color='red', alpha=0.2, label=f'±10% of Mean')

plt.xlabel('Event Number')
plt.ylabel('Total Signal Area')
plt.title('Scintillator Voltage vs. Signal Area')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

input("Press Enter to exit...")
