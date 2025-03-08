import pyvisa
import numpy as np
import csv
import time
import os
import matplotlib.pyplot as plt

# Initialize VISA resource manager
rm = pyvisa.ResourceManager()

# List available VISA devices
devices = rm.list_resources()
print("Available VISA Devices:", devices)

if not devices:
    raise Exception("No VISA devices found. Check oscilloscope connection.")

# Select the correct VISA resource dynamically
oscope = rm.open_resource(devices[0])  # Uses the first available device (update manually if needed)

# Test communication
oscope.write("*IDN?")
response = oscope.read()
print("Oscilloscope ID:", response)

# Define save directory
save_dir = "C:\\Users\\Swager\\OneDrive\\Desktop\\experiment_folder\\events"
os.makedirs(save_dir, exist_ok=True)  # Ensure directory exists

# Define event detection parameters
SCINTILLATOR_THRESHOLD = 2.2  # Voltage threshold for CH1 & CH2
SCINTILLATOR_DURATION = 3  # Number of consecutive points above threshold
SMDT_THRESHOLD = -30.0E-3  # Voltage threshold for CH3
SMDT_DELAY = 8.44E-10  # Expected time delay for CH3 (mean latency)
SMDT_WINDOW = 1.874E-10  # Increased window to 2x SEM  # Allowed time window for CH3 detection (SEM)
DEAD_TIME = 50E-6  # Ignore new events for 50µs

# Define collection settings
event_target = 1  # Stop after recording this many events
event_limit = 100  # Stop after this many waveform captures (set None for unlimited)
start_time = time.time()
event_count = 0

print("\n--- Starting Continuous Data Collection ---")

while event_count < event_target:
    if event_limit and event_count >= event_limit:
        break

    all_data = []
    timestamps = []
    channel_data = {1: [], 2: [], 3: []}
    
    # Acquire data for each channel
    for channel, name in [(1, "Scintillator 1"), (2, "Scintillator 2"), (3, "sMDT")]:
        oscope.write(f"DATa:SOUrce CH{channel}")
        oscope.write("DATa:ENCdg ASCII")
        oscope.write("DATa:WIDth 1")
        oscope.write("ACQuire:MODe SAMPLE")

        # Query scaling factors
        oscope.write("WFMPRe:YMUlt?")
        ymult = float(oscope.read())

        oscope.write("WFMPRe:YOFf?")
        yoff = float(oscope.read())

        oscope.write("WFMPRe:YZEro?")
        yzero = float(oscope.read())

        # Request waveform data
        oscope.write("CURVe?")
        raw_data = oscope.read()

        # Convert raw data to numeric values
        raw_waveform = np.array(raw_data.split(","), dtype=float)

        # Apply scaling conversion
        voltage_values = (raw_waveform - yoff) * ymult + yzero

        # Store data
        channel_data[channel] = voltage_values
        if channel == 1:
            timestamps = np.linspace(0, len(voltage_values) * 1e-9, len(voltage_values))  # Assuming 1 ns sample rate
    
    # Debugging: Print occurrences where CH1 & CH2 exceed threshold together
    coincident_events = np.where((channel_data[1] > SCINTILLATOR_THRESHOLD) & (channel_data[2] > SCINTILLATOR_THRESHOLD))[0]
    print(f"Number of CH1 & CH2 coincidences: {len(coincident_events)}")
    
    if len(coincident_events) > 0:
        for idx in coincident_events:
            if idx + SCINTILLATOR_DURATION < len(channel_data[1]) and all(channel_data[1][idx:idx+SCINTILLATOR_DURATION] > SCINTILLATOR_THRESHOLD) and all(channel_data[2][idx:idx+SCINTILLATOR_DURATION] > SCINTILLATOR_THRESHOLD):
                smdt_time = timestamps[idx] + SMDT_DELAY
                smdt_window_start = smdt_time - SMDT_WINDOW
                smdt_window_end = smdt_time + SMDT_WINDOW

                smdt_event_indices = np.where((timestamps >= smdt_window_start) & (timestamps <= smdt_window_end) & (channel_data[3] < SMDT_THRESHOLD))[0]

                if len(smdt_event_indices) > 0:
                    event_count += 1
                    event_filename = os.path.join(save_dir, f"Event_{event_count:03d}.csv")
                    with open(event_filename, "w", newline="") as event_file:
                        writer = csv.writer(event_file)
                        writer.writerow(["Time (s)", "CH1 (V)", "CH2 (V)", "sMDT (V)"])
                        for i in range(len(timestamps)):
                            writer.writerow([timestamps[i], channel_data[1][i], channel_data[2][i], channel_data[3][i]])
                    print(f"Event {event_count} recorded: {event_filename}")
                    
                    # Plot the waveform of the recorded event
                    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
                    axs[0].plot(timestamps, channel_data[1], label="CH1 (Scintillator 1)")
                    axs[1].plot(timestamps, channel_data[2], label="CH2 (Scintillator 2)")
                    axs[2].plot(timestamps, channel_data[3], label="CH3 (sMDT)")
                    axs[0].axhline(y=SCINTILLATOR_THRESHOLD, color='r', linestyle='--', label="CH1 & CH2 Threshold")
                    axs[2].axhline(y=SMDT_THRESHOLD, color='g', linestyle='--', label="CH3 Threshold")
                    axs[2].set_xlabel("Time (s)")
                    axs[1].set_ylabel("Voltage (V)")
                    fig.suptitle(f"Waveform for Event {event_count}")
                    for ax in axs: ax.legend()
                    for ax in axs: ax.grid()
                    plt.tight_layout()
plt.show()

print(f"\nData collection complete. {event_count} events recorded.")
print(f"Event files saved in: {save_dir}")
