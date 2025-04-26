print("Script is running...")

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import re

directory = r"C:\Users\colin\OneDrive\Desktop\Voltage Optimization Data"
print(f"Processing files in: {directory}")
print("Files in directory:", os.listdir(directory))

def extract_voltage(filename):
    match = re.search(r"(\d+)\s*V", filename)
    return int(match.group(1)) if match else None

def analyze_peak_and_timing(file_path):
    df = pd.read_csv(file_path, skiprows=17)
    try:
        df = df.iloc[:, [3, 4]]  # Columns D and E
        df.columns = ["Time (s)", "sMDT (V)"]
    except IndexError:
        print(f"Skipping {file_path}: Columns D and E not found.")
        return [], []

    df.dropna(inplace=True)
    df = df.apply(pd.to_numeric)

    baseline = df["sMDT (V)"].iloc[:200].mean()

    peak_voltages = []
    times_to_peak = []

    below_baseline = False
    start_index = None

    for i in range(len(df)):
        voltage = df["sMDT (V)"].iloc[i]
        if voltage < baseline:
            if not below_baseline:
                below_baseline = True
                start_index = i
        else:
            if below_baseline:
                below_baseline = False
                if start_index is not None:
                    event_df = df.iloc[start_index:i].copy()
                    event_df["Relative V"] = event_df["sMDT (V)"] - baseline

                    peak_idx = event_df["Relative V"].idxmin()
                    peak_voltage = event_df["Relative V"].loc[peak_idx]
                    time_to_peak = event_df["Time (s)"].loc[peak_idx] - event_df["Time (s)"].iloc[0]

                    peak_voltages.append(abs(peak_voltage))
                    times_to_peak.append(time_to_peak)

    return peak_voltages, times_to_peak

def process_all_files(directory):
    voltage_peaks = {}
    voltage_times = {}

    for file in os.listdir(directory):
        if file.endswith(".csv"):
            voltage = extract_voltage(file)
            if voltage is None:
                print(f"Skipping {file}: No voltage found in filename.")
                continue

            file_path = os.path.join(directory, file)
            peaks, times = analyze_peak_and_timing(file_path)

            if voltage not in voltage_peaks:
                voltage_peaks[voltage] = []
                voltage_times[voltage] = []

            voltage_peaks[voltage].extend(peaks)
            voltage_times[voltage].extend(times)

    if not voltage_peaks:
        print("No valid data found.")
        return

    rows = []
    for voltage in voltage_peaks:
        for peak, time in zip(voltage_peaks[voltage], voltage_times[voltage]):
            rows.append({"Voltage (V)": voltage, "Peak Voltage (V)": peak, "Time to Peak (s)": time})

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(directory, "sMDT_Peak_And_Timing_By_Voltage.csv"), index=False)
    print("Saved peak/timing data to CSV.")

    summary = df.groupby("Voltage (V)").agg({
        "Peak Voltage (V)": ["mean", "sem"],
        "Time to Peak (s)": ["mean", "sem"]
    })
    summary.columns = ["Peak Mean", "Peak SEM", "Time Mean", "Time SEM"]
    summary.reset_index(inplace=True)

    # Plot: Peak Voltage
    average_peak_sem = summary["Peak SEM"].mean()

    plt.figure(figsize=(10, 5))
    plt.bar(summary["Voltage (V)"], summary["Peak Mean"], yerr=summary["Peak SEM"],
            capsize=5, alpha=0.7, edgecolor='black', width=100,
            label=f"Mean ± SEM (avg SEM: ±{average_peak_sem:.2e} V)")

    plt.title("Mean Peak Voltage by Tube Voltage")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Peak Voltage Magnitude (V)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(directory, "sMDT_Peak_Voltage_vs_Voltage.png"), dpi=300)
    plt.show()

    # Plot: Time to Peak
    average_time_sem = summary["Time SEM"].mean()

    plt.figure(figsize=(10, 5))
    plt.bar(summary["Voltage (V)"], summary["Time Mean"], yerr=summary["Time SEM"],
            capsize=5, alpha=0.7, edgecolor='black', width=100,
            label=f"Mean ± SEM (avg SEM: ±{average_time_sem:.2e} s)")

    plt.title("Mean Time to Peak by Tube Voltage")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Time to Peak (s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(directory, "sMDT_Time_to_Peak_vs_Voltage.png"), dpi=300)
    plt.show()

# Run the script
process_all_files(directory)

input("Press Enter to exit...")
