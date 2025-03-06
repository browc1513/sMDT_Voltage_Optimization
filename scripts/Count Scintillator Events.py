print("Script is running...")

import pandas as pd
import os

# Define the directory path
directory = os.path.join(os.path.dirname(os.getcwd()), "raw_data", "Experiment_1_Raw_Data")
print(f"Processing files in: {directory}")
print("Files in directory:", os.listdir(directory))

# Function to count events exceeding threshold
def count_events(file_path, threshold=2.2):
    df = pd.read_csv(file_path, skiprows=17)  # Load CSV and skip initial rows
    df.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R']
    df = df[['D','E','K']]  # Select relevant columns
    df.columns = ["Time (s)", "CH1 (V)", "CH2 (V)"]
    df.dropna(inplace=True)  # Remove any NaN values
    df = df.apply(pd.to_numeric)  # Convert to numeric
    
    events = {'CH1 (V)': 0, 'CH2 (V)': 0}
    
    for channel in ["CH1 (V)", "CH2 (V)"]:
        above_threshold = False  # Tracks if we are inside an event
        for voltage in df[channel]:
            if voltage >= threshold:
                if not above_threshold:  # New event detected
                    events[channel] += 1
                    above_threshold = True
            else:
                above_threshold = False  # Reset when signal drops below threshold
    
    return events

# Process all CSV files in a directory
def process_all_files(directory):
    total_events = {'CH1 (V)': 0, 'CH2 (V)': 0}
    results = []
    
    for file in os.listdir(directory):
        if file.endswith(".csv"):  # Only process CSV files
            file_path = os.path.join(directory, file)
            events = count_events(file_path)
            total_events['CH1 (V)'] += events['CH1 (V)']
            total_events['CH2 (V)'] += events['CH2 (V)']
            results.append([file, events['CH1 (V)'], events['CH2 (V)']])
    
    # Create DataFrame for readable table output
    df_results = pd.DataFrame(results, columns=["Filename", "CH1 Events", "CH2 Events"])
    df_results.loc[len(df_results)] = ["Total", total_events['CH1 (V)'], total_events['CH2 (V)']]
    df_results["Total Events"] = df_results["CH1 Events"] + df_results["CH2 Events"]
    print("\nEvent Count Summary:")
    print(df_results.to_string(index=False))
    
# Run the function
process_all_files(directory)

input("Press Enter to exit...")
