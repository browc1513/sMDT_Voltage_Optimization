print("Script is running...")

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import re

# Define your data directory
directory = r"C:\Users\colin\OneDrive\Desktop\Voltage Optimization Data"
print(f"Processing files in: {directory}")
print("Files in directory:", os.listdir(directory))

# Function to extract voltage from filename (e.g., "3200 V - Capture 1.csv")
def extract_voltage(filename):
    match = re.search(r"(\d+)\s*V", filename)
    return int(match.group(1)) if match else None

# Function to compute signal area for sMDT events in a single file
def process_sMDT_signal_area(file_path):
    df = pd.read_csv(file_path, skiprows=17)
    available_columns = df.columns.tolist()

    try:
        df = df.iloc[:, [3, 4]]  # Columns D and E
        df.columns = ["Time (s)", "sMDT (V)"]
    except IndexError:
        print(f"Skipping {file_path}: Columns D and E not found.")
        return []

    df.dropna(inplace=True)
    df = df.apply(pd.to_numeric)

    # Calculate local baseline using first 200 points
    baseline = df["sMDT (V)"].iloc[:200].mean()

    event_areas = []
    below_baseline = False
    start_index = None

    for i in range(len(df)):
        if df["sMDT (V)"].iloc[i] < baseline:
            if not below_baseline:
                below_baseline = True
                start_index = i
        else:
            if below_baseline:
                below_baseline = False
                if start_index is not None:
                    time_values = df["Time (s)"].iloc[start_index:i].values
                    voltage_values = df["sMDT (V)"].iloc[start_index:i].values - baseline
                    delta_t = np.diff(time_values)
                    area = np.sum(voltage_values[:-1] * delta_t)
                    event_areas.append(abs(area))

    return event_areas

# Process all files and group by voltage
def process_all_files(directory):
    voltage_data = {}

    for file in os.listdir(directory):
        if file.endswith(".csv"):
            voltage = extract_voltage(file)
            if voltage is None:
                print(f"Skipping {file}: No voltage found in filename.")
                continue

            file_path = os.path.join(directory, file)
            areas = process_sMDT_signal_area(file_path)

            if voltage not in voltage_data:
                voltage_data[voltage] = []

            voltage_data[voltage].extend(areas)

    if not voltage_data:
        print("No valid signal area data found.")
        return

    # Build DataFrame for analysis
    voltage_list = []
    area_list = []

    for voltage, areas in voltage_data.items():
        for area in areas:
            voltage_list.append(voltage)
            area_list.append(area)

    df = pd.DataFrame({
        "Voltage (V)": voltage_list,
        "Signal Area (V·s)": area_list
    })

    df.to_csv(os.path.join(directory, "sMDT_Signal_Area_By_Voltage.csv"), index=False)
    print(f"Saved grouped signal area data to CSV.")

    # Compute stats per voltage
    summary = df.groupby("Voltage (V)")["Signal Area (V·s)"].agg(["mean", "sem"]).reset_index()

    # Get average SEM
    average_sem = summary["sem"].mean()

    # Plot
    plt.figure(figsize=(10, 6))
    plt.bar(
        summary["Voltage (V)"],
        summary["mean"],
        yerr=summary["sem"],
        width=100,
        capsize=5,
        alpha=0.7,
        edgecolor='black',
        label=f"Mean ± SEM (avg SEM: ±{average_sem:.2e} V·s)"
    )

    plt.title("Average sMDT Signal Area by Voltage")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Average Signal Area (V·s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save and show
    plot_path = os.path.join(directory, "sMDT_Signal_Area_By_Voltage.png")
    plt.savefig(plot_path, dpi=300)
    print(f"Saved plot to: {plot_path}")
    plt.show()

# Run the script
process_all_files(directory)

input("Press Enter to exit...")
