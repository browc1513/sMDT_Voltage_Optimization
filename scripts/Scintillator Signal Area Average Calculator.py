import pandas as pd
import numpy as np
import os

# Define the directory path
directory = os.path.join(os.getcwd(), "raw_data", "Experiment_1_Raw_Data")
print(f"Processing files in: {directory}")
print("Files in directory:", os.listdir(directory))

# List all the CSV files in the directory
files = [f for f in os.listdir(directory) if f.endswith('.csv')]

# Initialize variables to hold the sum of signal areas and count
total_ch1_area = 0
total_ch2_area = 0
total_combined_area = 0
file_count = 0

# Loop through each file and process
for file_name in files:
    file_path = os.path.join(directory, file_name)
    
    try:
        # Load Data
        df = pd.read_csv(file_path, skiprows=17)
        print(f"Columns in {file_name}: {df.columns.tolist()}")  # Print the columns of the file
        
        # Check if the expected columns exist, and adjust if necessary
        # Assuming CH1 and CH2 are present as unnamed columns
        # Adjust as needed after reviewing the printed column names
        df.columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']

        # Extract relevant columns
        df = df[['D', 'E', 'K']]  # Adjust column names based on what you see
        df.columns = ["Time (s)", "CH1 (V)", "CH2 (V)"]
        df.dropna(inplace=True)
        
        # Convert columns to numeric
        df["Time (s)"] = pd.to_numeric(df["Time (s)"])
        df["CH1 (V)"] = pd.to_numeric(df["CH1 (V)"])
        df["CH2 (V)"] = pd.to_numeric(df["CH2 (V)"])

        # Function to sum voltages above the threshold and calculate the average
        def calculate_signal_area(df, threshold=2.2):
            signal_areas_ch1 = []
            signal_areas_ch2 = []
            
            above_threshold = False  # Flag to track if we're inside an event
            start_index = None

            # Loop through the data to find all events
            for i in range(len(df)):
                if df["CH1 (V)"].iloc[i] > threshold and not above_threshold:
                    above_threshold = True
                    start_index = i  # Mark start of the event
                elif df["CH1 (V)"].iloc[i] < threshold and above_threshold:
                    above_threshold = False
                    # Now calculate the sum of voltages for this event
                    ch1_sum = df.loc[start_index:i, "CH1 (V)"].sum()
                    ch2_sum = df.loc[start_index:i, "CH2 (V)"].sum()
                    
                    signal_areas_ch1.append(ch1_sum)
                    signal_areas_ch2.append(ch2_sum)
            
            # Compute average sum for CH1 and CH2
            avg_ch1 = np.mean(signal_areas_ch1) if signal_areas_ch1 else 0
            avg_ch2 = np.mean(signal_areas_ch2) if signal_areas_ch2 else 0
            avg_total = (avg_ch1 + avg_ch2) / 2  # Average for both channels

            return avg_ch1, avg_ch2, avg_total

        # Calculate signal areas for CH1, CH2, and both channels combined
        avg_ch1, avg_ch2, avg_total = calculate_signal_area(df)

        # Add to the totals
        total_ch1_area += avg_ch1
        total_ch2_area += avg_ch2
        total_combined_area += avg_total
        file_count += 1

        # Output the results for each file
        print(f"Average Signal Area for {file_name} CH1 (V·s): {avg_ch1:.2e}")
        print(f"Average Signal Area for {file_name} CH2 (V·s): {avg_ch2:.2e}")
        print(f"Average Signal Area for {file_name} Both Channels Combined (V·s): {avg_total:.2e}")
    
    except Exception as e:
        print(f"Error processing {file_name}: {e}")

# Calculate averages for all files
average_ch1_area = total_ch1_area / file_count if file_count > 0 else 0
average_ch2_area = total_ch2_area / file_count if file_count > 0 else 0
average_combined_area = total_combined_area / file_count if file_count > 0 else 0

# Print the final results after processing all files
print(f"\nAverage Signal Area for CH1 (V·s): {average_ch1_area:.2e}")
print(f"Average Signal Area for CH2 (V·s): {average_ch2_area:.2e}")
print(f"Average Signal Area for Both Channels Combined (V·s): {average_combined_area:.2e}")

input("Press Enter to exit...") 
