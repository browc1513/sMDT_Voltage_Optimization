import os
import pandas as pd
import time

def monitor_muon_events(data_directory, experiment_duration, save_directory):
    """
    Monitors oscilloscope data in real-time, detects muon events, and saves each event as a .csv file.
    
    Parameters:
    - data_directory: Path where oscilloscope .csv files are stored.
    - experiment_duration: Total time (in seconds) to monitor the oscilloscope.
    - save_directory: Path to save detected event files.
    """
    start_time = time.time()
    event_count = 0
    
    while time.time() - start_time < experiment_duration:
        for file in os.listdir(data_directory):
            if file.endswith(".csv"):
                file_path = os.path.join(data_directory, file)
                
                try:
                    # Load the data, skipping metadata rows
                    df = pd.read_csv(file_path, skiprows=100)  # Adjust based on actual row of raw data
                    
                    # Rename columns for clarity
                    df = df[["D", "E", "K", "Q"]]
                    df.columns = ["Time (s)", "CH1 (V)", "CH2 (V)", "sMDT (V)"]
                    df = df.apply(pd.to_numeric, errors='coerce').dropna()
                    
                    # Check if a muon event occurred
                    ch1_trigger = df["CH1 (V)"] > 2.2
                    ch2_trigger = df["CH2 (V)"] > 2.2
                    smdt_trigger = df["sMDT (V)"] < -1.3e-3
                    
                    # Detect event where both CH1 & CH2 exceed 2.2V and sMDT drops below -1.3e-3V
                    event_indices = df.index[ch1_trigger & ch2_trigger & smdt_trigger].tolist()
                    
                    if event_indices:
                        event_count += 1
                        event_data = df.loc[event_indices]
                        event_filename = os.path.join(save_directory, f"Muon_Event_{event_count:04d}.csv")
                        event_data.to_csv(event_filename, index=False)
                        print(f"Muon event detected! Saved as {event_filename}")
                
                except Exception as e:
                    print(f"Error processing {file}: {e}")
        
        time.sleep(1)  # Adjust frequency of checking as needed
    
    print(f"Experiment complete! Total events detected: {event_count}")

# Example usage
experiment_folder = r"C:\Users\colin\OneDrive\Desktop\Experiment_Data"
output_folder = r"C:\Users\colin\OneDrive\Desktop\Detected_Events"
os.makedirs(output_folder, exist_ok=True)

monitor_muon_events(experiment_folder, experiment_duration=600, save_directory=output_folder)
