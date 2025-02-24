import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simpson
import os

# Define the directory path (updated for GitHub directory structure)
directory = os.path.join(os.getcwd(), "raw_data", "Experiment_1_Raw_Data")
print(f"Processing files in: {directory}")
files = [f for f in os.listdir(directory) if f.endswith('.csv')]  # List all .csv files
print("Files to process:", files)

# Function to sum voltages above the threshold and calculate the average
def calculate_signal_area(df, threshold=2.2):
    signal_areas_ch1 = []
    signal_areas_ch2 = []
    
    above_threshold = False  # Flag to track if we're inside an event
    start_index = None

    # Loop through the data to find all events
    for i in range(len(df)):
        if df["CH1 (V)"].iloc[i] > threshold and not above_threshold:
            above_threshold = True
            start_index = i  # Mark start of the event
        elif df["CH1 (V)"].iloc[i] < threshold and above_threshold:
            above_threshold = False
            # Now calculate the sum of voltages for this event
            ch1_sum = df.loc[start_index:i, "CH1 (V)"].sum()
            ch2_sum = df.loc[start_index:i, "CH2 (V)"].sum()
            
            signal_areas_ch1.append(ch1_sum)
            signal_areas_ch2.append(ch2_sum)
    
    # Compute average sum for CH1 and CH2
    avg_ch1 = np.mean(signal_areas_ch1) if signal_areas_ch1 else 0
    avg_ch2 = np.mean(signal_areas_ch2) if signal_areas_ch2 else 0
    avg_total = (avg_ch1 + avg_ch2) / 2  # Average for both channels

    return avg_ch1, avg_ch2, avg_total, signal_areas_ch1, signal_areas_ch2

# Initialize lists to store results
all_signal_areas_ch1 = []
all_signal_areas_ch2 = []

# Loop through all files in the directory and process them
for file_name in files:
    file_path = os.path.join(directory, file_name)
    
    # Load Data
    df = pd.read_csv(file_path, skiprows=17)
    
    # Correctly name the columns based on the provided script
    df.columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']
    df = df[['D', 'E', 'K']]  # Time, CH1, CH2
    df.columns = ["Time (s)", "CH1 (V)", "CH2 (V)"]  # Rename the columns to match our desired format
    df.dropna(inplace=True)

    # Convert columns to numeric
    df["Time (s)"] = pd.to_numeric(df["Time (s)"])
    df["CH1 (V)"] = pd.to_numeric(df["CH1 (V)"])
    df["CH2 (V)"] = pd.to_numeric(df["CH2 (V)"])

    # Calculate signal areas for CH1, CH2, and both channels combined
    avg_ch1, avg_ch2, avg_total, signal_areas_ch1, signal_areas_ch2 = calculate_signal_area(df)

    # Store the results
    all_signal_areas_ch1.extend(signal_areas_ch1)
    all_signal_areas_ch2.extend(signal_areas_ch2)

# Calculate the overall average signal areas for CH1, CH2, and combined
avg_ch1 = np.mean(all_signal_areas_ch1)
avg_ch2 = np.mean(all_signal_areas_ch2)
avg_total = (avg_ch1 + avg_ch2) / 2  # Average for both channels

# Calculate Standard Error of the Mean (SEM)
sem_ch1 = np.std(all_signal_areas_ch1) / np.sqrt(len(all_signal_areas_ch1)) if len(all_signal_areas_ch1) > 0 else 0
sem_ch2 = np.std(all_signal_areas_ch2) / np.sqrt(len(all_signal_areas_ch2)) if len(all_signal_areas_ch2) > 0 else 0
sem_total = np.std(np.array(all_signal_areas_ch1) + np.array(all_signal_areas_ch2)) / np.sqrt(len(all_signal_areas_ch1 + all_signal_areas_ch2)) if len(all_signal_areas_ch1 + all_signal_areas_ch2) > 0 else 0

# Output the results
print(f"Average Signal Area for CH1 (V·s): {avg_ch1:.2e}")
print(f"Average Signal Area for CH2 (V·s): {avg_ch2:.2e}")
print(f"Average Signal Area for Both Channels Combined (V·s): {avg_total:.2e}")

# Plot Histogram for Signal Areas (for CH1, CH2, and Combined)
plt.figure(figsize=(10, 6))

# Plot CH1 signal area distribution
plt.hist(all_signal_areas_ch1, bins=20, alpha=0.6, color='blue', label=f'CH1 Signal Area (mean: {avg_ch1:.2e}, SEM: {sem_ch1:.2e})')

# Plot CH2 signal area distribution
plt.hist(all_signal_areas_ch2, bins=20, alpha=0.6, color='purple', label=f'CH2 Signal Area (mean: {avg_ch2:.2e}, SEM: {sem_ch2:.2e})')

# Plot combined signal area distribution
combined_signal_areas = np.array(all_signal_areas_ch1) + np.array(all_signal_areas_ch2)
plt.hist(combined_signal_areas, bins=20, alpha=0.6, color='red', label=f'Combined Signal Area (mean: {avg_total:.2e}, SEM: {sem_total:.2e})')

# Add a vertical red dashed line for the mean of each distribution
plt.axvline(avg_ch1, color='blue', linestyle='--', linewidth=2)
plt.axvline(avg_ch2, color='purple', linestyle='--', linewidth=2)
plt.axvline(avg_total, color='red', linestyle='--', linewidth=2)

# Label the graph
plt.xlabel('Signal Area (V·s)')
plt.ylabel('Frequency')
plt.title('Distribution of Signal Areas')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the histogram
plt.show()

input("Press Enter to exit...")
