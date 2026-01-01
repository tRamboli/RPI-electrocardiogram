#!/usr/bin/env python3
"""
Raspberry Pi ECG Data Recorder
Reads ECG data from ADS1115 ADC and saves to file for offline plotting
"""

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Recording configuration
OUTPUT_FILE = "ecg_data.txt"
DURATION = 10  # seconds to record
SAMPLE_RATE = 0.005  # 0.01 = ~100 Hz, 0.005 = ~200 Hz, 0.002 = ~500 Hz

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus with address
# Default address is 0x48
try:
    ads = ADS.ADS1115(i2c, address=0x48)
    print(f"ADS1115 connected at address 0x48")
except Exception as e:
    print(f"Error connecting to ADS1115: {e}")
    print("Make sure the ADS1115 is properly connected:")
    print("  VDD → 3.3V")
    print("  GND → GND")
    print("  SCL → GPIO 3 (Pin 5)")
    print("  SDA → GPIO 2 (Pin 3)")
    exit(1)

# Optional: Set gain for better sensitivity
# ads.gain = 16  # ±0.256V range (most sensitive for small ECG signals)
# ads.gain = 8   # ±0.512V range
# ads.gain = 4   # ±1.024V range (default)
# ads.gain = 2   # ±2.048V range
# ads.gain = 1   # ±4.096V range

# Create single-ended input on channel 0
try:
    chan0 = AnalogIn(ads, 0)
    print(f"Reading from channel A0")
except Exception as e:
    print(f"Error setting up analog input: {e}")
    exit(1)

# For differential mode (recommended for ECG):
# Uncomment the following line and comment out the chan0 line above
# chan_diff = AnalogIn(ads, 0, 1)  # Differential between A0 and A1

print(f"Recording ECG data to {OUTPUT_FILE}")
print(f"Duration: {DURATION} seconds")
print(f"Sample rate: ~{1/SAMPLE_RATE:.0f} Hz")
print("Press Ctrl+C to stop early")

try:
    with open(OUTPUT_FILE, 'w') as f:
        # Write header
        f.write("# ECG Data Recording\n")
        f.write("# Format: sample_number,time(s),voltage(V)\n")
        f.write(f"# Sample rate: ~{1/SAMPLE_RATE:.0f} Hz\n")
        f.write(f"# Target duration: {DURATION} seconds\n")
        
        sample_count = 0
        start_time = time.time()
        
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            # Check if recording duration reached
            if elapsed_time >= DURATION:
                break
            
            # Read voltage
            voltage = chan0.voltage  # in volts
            
            # For differential mode, use:
            # voltage = chan.voltage
            
            # Write to file: sample_number,time,voltage
            f.write(f"{sample_count},{elapsed_time:.6f},{voltage:.6f}\n")
            
            sample_count += 1
            
            # Progress indicator
            if sample_count % 100 == 0:
                print(f"Recording... {elapsed_time:.1f}s / {DURATION}s ({sample_count} samples)")
            
            # Sleep for desired sample rate
            time.sleep(SAMPLE_RATE)
    
    print(f"\nRecording complete!")
    print(f"Total samples: {sample_count}")
    print(f"Actual duration: {elapsed_time:.3f} seconds")
    print(f"Actual sample rate: {sample_count/elapsed_time:.2f} Hz")
    print(f"Data saved to: {OUTPUT_FILE}")
    print(f"\nRun 'python3 rpi_plot_ecg.py' to visualize the data")

except KeyboardInterrupt:
    print(f"\nRecording stopped by user")
    print(f"Partial data saved to: {OUTPUT_FILE}")
