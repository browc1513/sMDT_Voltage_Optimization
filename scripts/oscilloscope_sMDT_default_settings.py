import pyvisa

# Initialize VISA resource manager
rm = pyvisa.ResourceManager()

# Open connection to oscilloscope (Replace with your actual VISA address)
oscope = rm.open_resource("USB0::0x0699::0x03A3::C031652::INSTR")

# Test communication
oscope.write("*IDN?")
response = oscope.read()
print("\nOscilloscope ID:", response)

print("\nSetting up oscilloscope with default sMDT settings...\n")

# ------------------ Configure Vertical (Y-Axis) Settings ------------------
oscope.write("CH1:SCAle 5.0")        # Set CH1 to 5V per division
oscope.write("CH1:POSition 1.86")    # Set CH1 vertical offset

oscope.write("CH2:SCAle 5.0")        # Set CH2 to 5V per division
oscope.write("CH2:POSition 1.00")    # Set CH2 vertical offset

oscope.write("CH3:SCAle 0.04")       # Set CH3 to 40mV per division
oscope.write("CH3:POSition -0.10")   # Set CH3 vertical offset

# ------------------ Configure Trigger Settings ------------------
oscope.write("TRIGger:A:EDGE:SOUrce CH3")  # Set trigger source to CH3
oscope.write("TRIGger:A:LEVel -0.04")      # Set trigger level to -40mV
oscope.write("TRIGger:A:TYPe EDGE")        # Set trigger type to EDGE

# ------------------ Configure Timebase (X-Axis) Settings ------------------
oscope.write("HORizontal:SCAle 10E-6")  # Set time scale to 10µs per division

# ------------------ Configure Acquisition Mode ------------------
oscope.write("ACQuire:MODe SAMPLE")  # Set acquisition mode to SAMPLE

print("\nOscilloscope setup complete. All default sMDT settings applied successfully.")
