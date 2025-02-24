print("Script is running...")

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# Define the directory path (updated for GitHub structure)
directory = os.path.join(os.getcwd(), "raw_data", "Experiment_1_Raw_Data")
print(f"Processing files in: {directory}")
print("Files in directory:", os.listdir(directory))

# Function to compute event durations
def process_event_durations(file_path, threshold=2.2):
    df = pd.read_csv(file_path, skiprows=17)  # Load CSV and skip initial rows
    df.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R']
    df = df[['D','E','K']]  # Select relevant columns
    df.columns = ["Time (s)", "CH1 (V)", "CH2 (V)"]
    df.dropna(inplace=True)  # Remove any NaN values
    df = df.apply(pd.to_numeric)  # Convert to numeric
    
    event_durations = {"CH1 (s)": [], "CH2 (s)": []}
    
    for channel in ["CH1 (V)", "CH2 (V)"]:
        above_threshold = False  # Tracks if we are inside an event
        start_time = None  # Start time of an event
        
        for i in range(len(df)):
            if df[channel].iloc[i] >= threshold:
                if not above_threshold:  # New event detected
                    above_threshold = True
                    start_time = df["Time (s)"].iloc[i]  # Mark start time
            else:
                if above_threshold:  # End of event
                    above_threshold = False
                    if start_time is not None:
                        end_time = df["Time (s)"].iloc[i]  # Mark end time
                        duration = end_time - start_time
                        event_durations[channel.replace("(V)", "(s)")].append(duration)
    
    return event_durations

# Process all CSV files in a directory and collect event durations
def process_all_files(directory):
    all_durations = {"CH1 (s)": [], "CH2 (s)": []}
    
    for file in os.listdir(directory):
        if file.endswith(".csv"):  # Only process CSV files
            
            # Skip Signal_Area_Summary.csv if it doesn't match the expected structure
            if file == "Signal_Area_Summary.csv":
                print(f"Skipping {file} due to unexpected structure.")
                continue
            
            file_path = os.path.join(directory, file)
            event_durations = process_event_durations(file_path)
            all_durations["CH1 (s)"].extend(event_durations["CH1 (s)"])
            all_durations["CH2 (s)"].extend(event_durations["CH2 (s)"])
    
    # Compute and print average durations
    mean_ch1 = np.mean(all_durations["CH1 (s)"])
    mean_ch2 = np.mean(all_durations["CH2 (s)"])
    print(f"\nAverage Event Duration:")
    print(f"CH1: {mean_ch1:.2e} s")
    print(f"CH2: {mean_ch2:.2e} s")
    
    # Plot histogram (distribution curve)
    plt.figure(figsize=(10, 5))
    plt.hist(all_durations["CH1 (s)"], bins=30, color='blue', alpha=0.7, edgecolor='black', label='CH1')
    plt.hist(all_durations["CH2 (s)"], bins=30, color='green', alpha=0.7, edgecolor='black', label='CH2')
    
    plt.xlabel("Event Duration (s)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Event Durations")
    plt.legend()
    plt.grid(True)
    plt.show()

# Run the function
process_all_files(directory)

input("Press Enter to exit...")
