print("Script is running...")

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# Define the directory path
directory = os.path.join(os.getcwd(), "raw_data", "Experiment_1_Raw_Data")
print(f"Processing files in: {directory}")
print("Files in directory:", os.listdir(directory))

# Function to find sMDT peak voltages
def process_sMDT(file_path):
    df = pd.read_csv(file_path, skiprows=17)  # Load CSV and skip initial rows
    print(f"Processing file: {file_path}, Columns found: {df.columns.tolist()}")  # Debugging output

    # Dynamically detect and rename columns
    expected_columns = ["D", "Q"]  # Time (s) and sMDT (V)
    available_columns = df.columns.tolist()

    # Check if expected columns exist, otherwise adjust
    if len(available_columns) >= max([ord(c) - ord('A') for c in expected_columns]) + 1:
        df = df.iloc[:, [ord(c) - ord('A') for c in expected_columns]]
        df.columns = ["Time (s)", "sMDT (V)"]
    else:
        print(f"Skipping {file_path}: Columns D and Q not found.")
        return []

    df.dropna(inplace=True)  # Remove any NaN values
    df = df.apply(pd.to_numeric)  # Convert to numeric

    # Find peak negative voltages (most negative values per event)
    peak_voltages = []

    above_threshold = False
    start_index = None

    for i in range(len(df)):
        if df["sMDT (V)"].iloc[i] < 0:  # sMDT signal should be negative
            if not above_threshold:
                above_threshold = True
                start_index = i
        else:
            if above_threshold:  # End of an event
                above_threshold = False
                if start_index is not None:
                    event_data = df["sMDT (V)"].iloc[start_index:i]
                    peak_voltage = np.min(event_data)  # Most negative value
                    peak_voltages.append(peak_voltage)

    return peak_voltages

# Process all CSV files in a directory
def process_all_files(directory):
    all_peaks = []

    for file in os.listdir(directory):
        if file.endswith(".csv"):  # Only process CSV files
            file_path = os.path.join(directory, file)
            peaks = process_sMDT(file_path)
            all_peaks.extend(peaks)

    if not all_peaks:
        print("No valid peak voltage data found. Exiting...")
        return

    # Convert to DataFrame and save to CSV
    df_peaks = pd.DataFrame({"sMDT Peak Voltage (V)": all_peaks})
    output_file = os.path.join(directory, "sMDT_Peak_Voltage_Summary.csv")
    df_peaks.to_csv(output_file, index=False)
    print(f"\nPeak voltage summary saved to: {output_file}")

    # Compute statistics
    mean_peak = np.mean(all_peaks)
    sem_peak = np.std(all_peaks) / np.sqrt(len(all_peaks))

    # Plot histogram
    plt.figure(figsize=(10, 5))
    plt.hist(all_peaks, bins=30, color='blue', alpha=0.7, edgecolor='black', label='sMDT Peaks')

    # Add average line
    plt.axvline(mean_peak, color='red', linestyle='dashed', label=f'Mean: {mean_peak:.2e} V')

    # Add error bars
    plt.fill_betweenx([0, plt.ylim()[1]], mean_peak - sem_peak, mean_peak + sem_peak, color='red', alpha=0.2, label=f'SEM: {sem_peak:.2e} V')

    plt.xlabel("sMDT Peak Voltage (V)")
    plt.ylabel("Frequency")
    plt.title("Histogram of sMDT Peak Voltages")
    plt.legend()
    plt.grid(True)
    plt.show()

# Run the function
process_all_files(directory)

input("Press Enter to exit...")
