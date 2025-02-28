print("Script is running...")

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# Define the directory path
directory = os.path.join(os.getcwd(), "raw_data", "Experiment_1_Raw_Data")
print(f"Processing files in: {directory}")
print("Files in directory:", os.listdir(directory))

# Function to compute signal area for sMDT events
def process_sMDT_signal_area(file_path):
    df = pd.read_csv(file_path, skiprows=17)  # Load CSV and skip initial rows
    print(f"Processing file: {file_path}, Columns found: {df.columns.tolist()}")  # Debugging output

    # Dynamically detect and rename columns
    expected_columns = ["D", "Q"]  # Time (s) and sMDT (V)
    available_columns = df.columns.tolist()

    # Check if expected columns exist
    if len(available_columns) >= max([ord(c) - ord('A') for c in expected_columns]) + 1:
        df = df.iloc[:, [ord(c) - ord('A') for c in expected_columns]]
        df.columns = ["Time (s)", "sMDT (V)"]
    else:
        print(f"Skipping {file_path}: Columns D and Q not found.")
        return []

    df.dropna(inplace=True)  # Remove any NaN values
    df = df.apply(pd.to_numeric)  # Convert to numeric

    # Compute signal area per event using Riemann sums
    event_areas = []
    above_threshold = False
    start_index = None

    for i in range(len(df)):
        if df["sMDT (V)"].iloc[i] < 0:  # Detect negative voltage event
            if not above_threshold:
                above_threshold = True
                start_index = i
        else:
            if above_threshold:  # End of an event
                above_threshold = False
                if start_index is not None:
                    time_values = df["Time (s)"].iloc[start_index:i].values
                    voltage_values = df["sMDT (V)"].iloc[start_index:i].values
                    delta_t = np.diff(time_values)  # Time step differences
                    area = np.sum(voltage_values[:-1] * delta_t)  # Riemann sum integration
                    event_areas.append(abs(area))  # Use absolute value to standardize

    return event_areas

# Process all CSV files in a directory
def process_all_files(directory):
    all_areas = []

    for file in os.listdir(directory):
        if file.endswith(".csv"):  # Only process CSV files
            file_path = os.path.join(directory, file)
            areas = process_sMDT_signal_area(file_path)
            all_areas.extend(areas)

    if not all_areas:
        print("No valid signal area data found. Exiting...")
        return

    # Convert to DataFrame and save to CSV
    df_areas = pd.DataFrame({"sMDT Signal Area (V·s)": all_areas})
    output_file = os.path.join(directory, "sMDT_Signal_Area_Summary.csv")
    df_areas.to_csv(output_file, index=False)
    print(f"\nSignal area summary saved to: {output_file}")

    # Compute statistics
    mean_area = np.mean(all_areas)
    sem_area = np.std(all_areas) / np.sqrt(len(all_areas))

    # Plot histogram
    plt.figure(figsize=(10, 5))
    plt.hist(all_areas, bins=30, color='blue', alpha=0.7, edgecolor='black', label='sMDT Signal Areas')

    # Add average line
    plt.axvline(mean_area, color='red', linestyle='dashed', label=f'Mean: {mean_area:.2e} V·s')

    # Add error bars
    plt.fill_betweenx([0, plt.ylim()[1]], mean_area - sem_area, mean_area + sem_area, color='red', alpha=0.2, label=f'SEM: ±{sem_area:.2e} V·s')

    plt.xlabel("sMDT Signal Area (V·s)")
    plt.ylabel("Frequency")
    plt.title("Histogram of sMDT Signal Areas")
    plt.legend()
    plt.grid(True)
    plt.show()

# Run the function
process_all_files(directory)

input("Press Enter to exit...")
