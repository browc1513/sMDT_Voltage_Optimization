print("Script is running...")

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

# Define paths
data_directory = os.path.join(os.getcwd(), "raw_data", "Experiment_1_Raw_Data")
desktop_path = r"C:\Users\colin\OneDrive\Desktop"
summary_output_file = os.path.join(desktop_path, "Muon_Analysis_Summary.csv")

print(f"Processing summary statistics from: {data_directory}")
print(f"Summary CSV will be saved to: {summary_output_file}")

# Load processed data files
peak_voltage_file = os.path.join(data_directory, "sMDT_Peak_Voltage_Summary.csv")
signal_area_file = os.path.join(data_directory, "sMDT_Signal_Area_Summary.csv")
latency_file = os.path.join(data_directory, "sMDT_Event_Latency_Summary.csv")

# Function to compute mean and SEM
def compute_stats(data):
    mean_val = np.mean(data)
    sem_val = np.std(data) / np.sqrt(len(data))
    return mean_val, sem_val

# Function to plot histograms
def plot_histogram(data, title, xlabel, filename):
    mean_val, sem_val = compute_stats(data)

    plt.figure(figsize=(10, 5))
    plt.hist(data, bins=30, color='blue', alpha=0.7, edgecolor='black', label=title)

    # Add average line
    plt.axvline(mean_val, color='red', linestyle='dashed', label=f'Mean: {mean_val:.2e}')

    # Add SEM shading
    plt.fill_betweenx([0, plt.ylim()[1]], mean_val - sem_val, mean_val + sem_val, 
                      color='red', alpha=0.2, label=f'SEM: ±{sem_val:.2e}')

    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    
    # Save the plot to Desktop
    plot_output_file = os.path.join(desktop_path, filename)
    plt.savefig(plot_output_file)
    print(f"Histogram saved to: {plot_output_file}")

    plt.show()

# Dictionary to store statistics
stats_summary = {}

# Process sMDT Peak Voltage
if os.path.exists(peak_voltage_file):
    df_peak = pd.read_csv(peak_voltage_file)
    if not df_peak.empty:
        mean_peak, sem_peak = compute_stats(df_peak["sMDT Peak Voltage (V)"])
        stats_summary["sMDT Peak Voltage (V)"] = [mean_peak, sem_peak]
        plot_histogram(df_peak["sMDT Peak Voltage (V)"], 
                       "Histogram of sMDT Peak Voltages", 
                       "sMDT Peak Voltage (V)", 
                       "sMDT_Peak_Voltage_Histogram.png")
    else:
        print("Warning: sMDT Peak Voltage file is empty.")
else:
    print("Warning: sMDT Peak Voltage file not found.")

# Process sMDT Signal Area
if os.path.exists(signal_area_file):
    df_area = pd.read_csv(signal_area_file)
    if not df_area.empty:
        mean_area, sem_area = compute_stats(df_area["sMDT Signal Area (V·s)"])
        stats_summary["sMDT Signal Area (V·s)"] = [mean_area, sem_area]
        plot_histogram(df_area["sMDT Signal Area (V·s)"], 
                       "Histogram of sMDT Signal Areas", 
                       "sMDT Signal Area (V·s)", 
                       "sMDT_Signal_Area_Histogram.png")
    else:
        print("Warning: sMDT Signal Area file is empty.")
else:
    print("Warning: sMDT Signal Area file not found.")

# Process Muon Event Latency
if os.path.exists(latency_file):
    df_latency = pd.read_csv(latency_file)
    if not df_latency.empty:
        mean_latency, sem_latency = compute_stats(df_latency["Muon Event Latency (s)"])
        stats_summary["Muon Event Latency (s)"] = [mean_latency, sem_latency]
        plot_histogram(df_latency["Muon Event Latency (s)"], 
                       "Histogram of Muon Event Latencies", 
                       "Muon Event Latency (s)", 
                       "Muon_Event_Latency_Histogram.png")
    else:
        print("Warning: Muon Event Latency file is empty.")
else:
    print("Warning: Muon Event Latency file not found.")

# Convert to DataFrame and save results to Desktop
df_summary = pd.DataFrame.from_dict(stats_summary, orient='index', columns=["Mean", "SEM"])
df_summary.to_csv(summary_output_file, index=True)

# Display results
print("\nFinal Summary of Muon Event Statistics:")
print(df_summary)

print(f"\nSummary saved to: {summary_output_file}")

input("Press Enter to exit...")
