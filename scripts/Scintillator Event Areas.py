print("Script is running...")

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# Define the directory path
directory = os.path.join(os.getcwd(), "raw_data", "Experiment_1_Raw_Data")
print(f"Processing files in: {directory}")
print("Files in directory:", os.listdir(directory))

# Function to count events and compute signal areas
def process_events(file_path, threshold=2.2):
    df = pd.read_csv(file_path, skiprows=17)  # Load CSV and skip initial rows
    df.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R']
    df = df[['D','E','K']]  # Select relevant columns
    df.columns = ["Time (s)", "CH1 (V)", "CH2 (V)"]
    df.dropna(inplace=True)  # Remove any NaN values
    df = df.apply(pd.to_numeric)  # Convert to numeric
    
    event_areas = {"CH1 (V)": [], "CH2 (V)": []}
    
    for channel in ["CH1 (V)", "CH2 (V)"]:
        above_threshold = False  # Tracks if we are inside an event
        start_index = None  # Start index of an event
        
        for i in range(len(df)):
            if df[channel].iloc[i] >= threshold:
                if not above_threshold:  # New event detected
                    above_threshold = True
                    start_index = i  # Mark start of event
            else:
                if above_threshold:  # End of event
                    above_threshold = False
                    if start_index is not None:
                        # Compute signal area using Riemann sum
                        time_values = df["Time (s)"].iloc[start_index:i].values
                        voltage_values = df[channel].iloc[start_index:i].values
                        delta_t = np.diff(time_values)  # Time step differences
                        area = np.sum(voltage_values[:-1] * delta_t)  # Riemann sum
                        event_areas[channel].append(area)
    
    return event_areas

# Process all CSV files in a directory and collect signal areas
def process_all_files(directory):
    all_areas = {"CH1 (V)": [], "CH2 (V)": []}
    
    for file in os.listdir(directory):
        if file.endswith(".csv"):  # Only process CSV files
            file_path = os.path.join(directory, file)
            event_areas = process_events(file_path)
            all_areas["CH1 (V)"].extend(event_areas["CH1 (V)"])
            all_areas["CH2 (V)"].extend(event_areas["CH2 (V)"])
    
    # Convert to DataFrame and save to CSV
    df_areas = pd.DataFrame({"CH1 Area (V·s)": all_areas["CH1 (V)"], "CH2 Area (V·s)": all_areas["CH2 (V)"]})
    output_file = os.path.join(directory, "Signal_Area_Summary.csv")
    df_areas.to_csv(output_file, index=False)
    print(f"\nSignal area summary saved to: {output_file}")
    
    # Compute statistics
    mean_ch1 = np.mean(all_areas["CH1 (V)"])
    mean_ch2 = np.mean(all_areas["CH2 (V)"])
    sem_ch1 = np.std(all_areas["CH1 (V)"]) / np.sqrt(len(all_areas["CH1 (V)"]))
    sem_ch2 = np.std(all_areas["CH2 (V)"]) / np.sqrt(len(all_areas["CH2 (V)"]))
    
    # Plot histograms
    plt.figure(figsize=(10, 5))
    plt.hist(all_areas["CH1 (V)"], bins=30, color='blue', alpha=0.7, edgecolor='black', label='CH1')
    plt.hist(all_areas["CH2 (V)"], bins=30, color='green', alpha=0.7, edgecolor='black', label='CH2')
    
    # Add average lines
    plt.axvline(mean_ch1, color='red', linestyle='dashed', label=f'CH1 Mean: {mean_ch1:.2e} V·s')
    plt.axvline(mean_ch2, color='purple', linestyle='dashed', label=f'CH2 Mean: {mean_ch2:.2e} V·s')
    
    # Add error bars
    plt.fill_betweenx([0, plt.ylim()[1]], mean_ch1 - sem_ch1, mean_ch1 + sem_ch1, color='red', alpha=0.2, label=f'CH1 SEM: {sem_ch1:.2e} V·s')
    plt.fill_betweenx([0, plt.ylim()[1]], mean_ch2 - sem_ch2, mean_ch2 + sem_ch2, color='purple', alpha=0.2, label=f'CH2 SEM: {sem_ch2:.2e} V·s')
    
    plt.xlabel("Signal Area (V·s)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Signal Areas")
    plt.legend()
    plt.grid(True)
    plt.show()
    
# Run the function
process_all_files(directory)

input("Press Enter to exit...")
