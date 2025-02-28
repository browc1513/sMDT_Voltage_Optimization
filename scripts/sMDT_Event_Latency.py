print("Script is running...")

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# Define the directory path
directory = os.path.join(os.getcwd(), "raw_data", "Experiment_1_Raw_Data")
print(f"Processing files in: {directory}")
print("Files in directory:", os.listdir(directory))

# Function to compute event latency
def process_sMDT_latency(file_path, threshold=2.2):
    df = pd.read_csv(file_path, skiprows=17)  # Load CSV and skip initial rows
    print(f"Processing file: {file_path}, Columns found: {df.columns.tolist()}")  # Debugging output

    # Dynamically detect and rename columns
    expected_columns = ["D", "E", "K", "Q"]  # Time, CH1, CH2, sMDT
    available_columns = df.columns.tolist()

    # Check if expected columns exist
    if len(available_columns) >= max([ord(c) - ord('A') for c in expected_columns]) + 1:
        df = df.iloc[:, [ord(c) - ord('A') for c in expected_columns]]
        df.columns = ["Time (s)", "CH1 (V)", "CH2 (V)", "sMDT (V)"]
    else:
        print(f"Skipping {file_path}: Required columns not found.")
        return []

    df.dropna(inplace=True)  # Remove any NaN values
    df = df.apply(pd.to_numeric)  # Convert to numeric

    # Find time difference between scintillator event and sMDT response
    event_latencies = []
    scintillator_triggered = False
    scintillator_time = None

    for i in range(len(df)):
        if df["CH1 (V)"].iloc[i] > threshold and df["CH2 (V)"].iloc[i] > threshold:
            if not scintillator_triggered:
                scintillator_triggered = True
                scintillator_time = df["Time (s)"].iloc[i]

        if scintillator_triggered and df["sMDT (V)"].iloc[i] < 0:  # First negative sMDT signal
            sMDT_time = df["Time (s)"].iloc[i]
            latency = sMDT_time - scintillator_time
            event_latencies.append(latency)
            scintillator_triggered = False  # Reset for next event

    return event_latencies

# Process all CSV files in a directory
def process_all_files(directory):
    all_latencies = []

    for file in os.listdir(directory):
        if file.endswith(".csv"):  # Only process CSV files
            file_path = os.path.join(directory, file)
            latencies = process_sMDT_latency(file_path)
            all_latencies.extend(latencies)

    if not all_latencies:
        print("No valid event latency data found. Exiting...")
        return

    # Convert to DataFrame and save to CSV
    df_latencies = pd.DataFrame({"Muon Event Latency (s)": all_latencies})
    output_file = os.path.join(directory, "sMDT_Event_Latency_Summary.csv")
    df_latencies.to_csv(output_file, index=False)
    print(f"\nEvent latency summary saved to: {output_file}")

    # Compute statistics
    mean_latency = np.mean(all_latencies)
    sem_latency = np.std(all_latencies) / np.sqrt(len(all_latencies))

    # Plot histogram
    plt.figure(figsize=(10, 5))
    plt.hist(all_latencies, bins=30, color='blue', alpha=0.7, edgecolor='black', label='Muon Event Latencies')

    # Add average line
    plt.axvline(mean_latency, color='red', linestyle='dashed', label=f'Mean: {mean_latency:.2e} s')

    # Add error bars
    plt.fill_betweenx([0, plt.ylim()[1]], mean_latency - sem_latency, mean_latency + sem_latency, color='red', alpha=0.2, label=f'SEM: ±{sem_latency:.2e} s')

    plt.xlabel("Muon Event Latency (s)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Muon Event Latencies")
    plt.legend()
    plt.grid(True)
    plt.show()

# Run the function
process_all_files(directory)

input("Press Enter to exit...")
