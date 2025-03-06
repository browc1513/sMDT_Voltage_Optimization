import pyvisa
import time
import pandas as pd
import os
import numpy as np

# Connect to oscilloscope
rm = pyvisa.ResourceManager()
scope = rm.open_resource('USB0::0x0699::0x03A3::C031652::INSTR')

# Get scaling factors
ymult_ch1 = float(scope.query('WFMPRE:YMULT?'))  # CH1 scale
yzero_ch1 = float(scope.query('WFMPRE:YZERO?'))
yoff_ch1 = float(scope.query('WFMPRE:YOFF?'))

ymult_ch2 = float(scope.query('WFMPRE:YMULT?'))  # CH2 scale
yzero_ch2 = float(scope.query('WFMPRE:YZERO?'))
yoff_ch2 = float(scope.query('WFMPRE:YOFF?'))

# Print scaling factors for debugging
print(f"CH1 Scaling Factors: ymult={ymult_ch1}, yzero={yzero_ch1}, yoff={yoff_ch1}")
print(f"CH2 Scaling Factors: ymult={ymult_ch2}, yzero={yzero_ch2}, yoff={yoff_ch2}")

# Configure waveform retrieval
scope.write('DATA:WIDTH 1')
scope.write('DATA:ENC RIB')

# Define event detection parameters
EVENT_THRESHOLD = 2.2  # Voltage threshold for both CH1 & CH2
SPIKE_THRESHOLD = 1.0  # Minimum sudden voltage change (ΔV) to detect a spike
EVENT_COOLDOWN = 1  # Minimum time (in seconds) between events
RUN_TIME = 60  # Total monitoring duration
SAVE_PATH = r"C:\Users\Swager\OneDrive\Desktop\experiment_folder"  # Path to save events

# Ensure save directory exists
os.makedirs(SAVE_PATH, exist_ok=True)

print("Monitoring for muon events with CH1 & CH2 coincidence and ΔV/Δt spike detection...")

start_time = time.time()
last_event_time = 0  # Track last event time to enforce cooldown
prev_max_ch1 = 0  # Track previous frame voltage for CH1
prev_max_ch2 = 0  # Track previous frame voltage for CH2
event_count = 0  # Track number of events recorded

try:
    while time.time() - start_time < RUN_TIME:
        # Get CH1 data
        scope.write('DATA:SOU CH1')
        raw_data_ch1 = scope.query_binary_values('CURVe?', datatype='B', container=list)
        voltages_ch1 = [(ymult_ch1 * (point - yoff_ch1)) + yzero_ch1 for point in raw_data_ch1]

        # Get CH2 data
        scope.write('DATA:SOU CH2')
        raw_data_ch2 = scope.query_binary_values('CURVe?', datatype='B', container=list)
        voltages_ch2 = [(ymult_ch2 * (point - yoff_ch2)) + yzero_ch2 for point in raw_data_ch2]

        # Compute rate of change (ΔV/Δt)
        dV_ch1 = np.diff(voltages_ch1, prepend=voltages_ch1[0])  # ΔV for CH1
        dV_ch2 = np.diff(voltages_ch2, prepend=voltages_ch2[0])  # ΔV for CH2

        # Print raw and converted data for debugging (first 10 values)
        print(f"Raw CH1 Data: {raw_data_ch1[:10]}")
        print(f"Converted CH1 Voltages: {voltages_ch1[:10]}")
        print(f"Raw CH2 Data: {raw_data_ch2[:10]}")
        print(f"Converted CH2 Voltages: {voltages_ch2[:10]}")
        
        # Find max voltage in the frame
        max_ch1 = max(voltages_ch1)
        max_ch2 = max(voltages_ch2)
        print(f"Max Voltage CH1: {max_ch1:.3f} V | Max Voltage CH2: {max_ch2:.3f} V")

        # Detect voltage spikes
        spike_ch1 = max(abs(dV_ch1)) > SPIKE_THRESHOLD
        spike_ch2 = max(abs(dV_ch2)) > SPIKE_THRESHOLD

        # Event Detection: Coincidence condition (Both CH1 & CH2 must cross threshold + detect spike)
        if (max_ch1 > EVENT_THRESHOLD and max_ch2 > EVENT_THRESHOLD and
                prev_max_ch1 <= EVENT_THRESHOLD and prev_max_ch2 <= EVENT_THRESHOLD and
                spike_ch1 and spike_ch2):
            current_time = time.time()
            if current_time - last_event_time > EVENT_COOLDOWN:
                event_count += 1
                last_event_time = current_time  # Reset cooldown timer

                # Save event data to CSV
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                event_filename = os.path.join(SAVE_PATH, f"Muon_Event_{event_count:04d}_{timestamp}.csv")

                # Create DataFrame and save
                df = pd.DataFrame({
                    "Time Index": range(len(voltages_ch1)),
                    "Voltage CH1 (V)": voltages_ch1,
                    "Voltage CH2 (V)": voltages_ch2,
                    "ΔV CH1 (V/sample)": dV_ch1,
                    "ΔV CH2 (V/sample)": dV_ch2
                })
                df.to_csv(event_filename, index=False)

                print(f"Muon event detected! Saved as {event_filename}")

        # Store previous frame voltage
        prev_max_ch1 = max_ch1
        prev_max_ch2 = max_ch2

        # Adjust sleep time for better resolution
        time.sleep(0.1)  # Faster polling rate

except KeyboardInterrupt:
    print("\nStopping monitoring.")

# Close oscilloscope connection
scope.close()
print("Experiment finished.")
