import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# Folder Setup
directory = os.path.join(os.getcwd(), "raw_data", "Experiment_1_Raw_Data")

if not os.path.isdir(folder_path):
    print(f"Directory does not exist: {folder_path}")
    exit()

csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
if not csv_files:
    print("No CSV files found in the specified directory. Exiting...")
    exit()

dataframes = {'Scintillator 1': [], 'Scintillator 2': [], 'sMDT': []}

# Step 1: Process Files
for file in csv_files:
    try:
        df_raw = pd.read_csv(file, skiprows=17)
        df_raw.columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']

        # Extract relevant data
        scint1 = df_raw[['D', 'E']].dropna()
        scint2 = df_raw[['J', 'K']].dropna()
        smdt = df_raw[['P', 'Q']].dropna()

        scint1.columns = ['Time', 'Amplitude']
        scint2.columns = ['Time', 'Amplitude']
        smdt.columns = ['Time', 'Amplitude']

        scint1['Source'] = os.path.basename(file)
        scint2['Source'] = os.path.basename(file)
        smdt['Source'] = os.path.basename(file)

        dataframes['Scintillator 1'].append(scint1)
        dataframes['Scintillator 2'].append(scint2)
        dataframes['sMDT'].append(smdt)
    except Exception as e:
        print(f"Error processing file {file}: {e}")

# Step 2: Combine Data
combined = {}
overall_metrics = {}
for key, dfs in dataframes.items():
    if dfs:
        combined[key] = pd.concat(dfs, ignore_index=True)
        combined[key]['Time'] = pd.to_numeric(combined[key]['Time'], errors='coerce')
        combined[key]['Amplitude'] = pd.to_numeric(combined[key]['Amplitude'], errors='coerce')
        combined[key] = combined[key].dropna()

# Step 3: Calculate Metrics
aggregated = {}
for key, df in combined.items():
    df['Time_Diff'] = df['Time'].diff()
    df['Area'] = 0.5 * (df['Amplitude'] + df['Amplitude'].shift(-1)) * df['Time_Diff']
    agg = df.groupby('Source').agg(
        Total_Area=('Area', 'sum'),
        Avg_Amplitude=('Amplitude', 'mean'),
        Std_Dev_Amplitude=('Amplitude', 'std')
    ).reset_index()
    aggregated[key] = agg

    # Calculate overall mean and std deviation for the entire dataset
    overall_mean = agg['Total_Area'].mean()
    overall_std = agg['Total_Area'].std()
    overall_metrics[key] = {'mean': overall_mean, 'std_dev': overall_std}

# Step 4: Generate Bar Graphs
for key, agg in aggregated.items():
    # Replace labels with numeric indices
    agg['Numeric_Label'] = range(1, len(agg) + 1)

    # Retrieve overall mean and std deviation
    overall_mean = overall_metrics[key]['mean']
    overall_std = overall_metrics[key]['std_dev']

    # Bar Plot with Mean and Std Dev
    plt.figure(figsize=(14, 7))
    plt.bar(
        agg['Numeric_Label'],
        agg['Total_Area'],
        color='blue',  # Changed to blue
        alpha=0.7,
        label=f'{key} Signal Area'
    )
    plt.axhline(y=overall_mean, color='red', linestyle='--', label=f'Overall Mean: {overall_mean:.2e}')
    plt.fill_between(
        agg['Numeric_Label'],
        overall_mean - overall_std,
        overall_mean + overall_std,
        color='red',
        alpha=0.2,
        label=f'±1 Std Dev: {overall_std:.2e}'
    )

    # Annotate overall mean on the graph
    plt.text(
        len(agg) - 1, overall_mean + (overall_std * 0.5),
        f"Mean: {overall_mean:.2e}",
        color='red',
        fontsize=10
    )

    plt.xlabel('Event Number')
    plt.ylabel('Total Signal Area')
    plt.title(f'{key} - Voltage vs. Signal Area')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

input("Press Enter to exit...")
