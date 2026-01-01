#!/usr/bin/env python3
"""
Raspberry Pi ECG Data Sender
Reads ECG data from ADS1115 ADC and streams via UDP to a remote server
"""

import time
import socket
import struct
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# UDP configuration
UDP_PORT = 5006
TARGET_IP = "127.0.0.1"  # localhost

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus with address
# Default address is 0x48
try:
    ads = ADS.ADS1115(i2c, address=0x48)
    print(f"ADS1115 connected at address 0x48")
except Exception as e:
    print(f"Error connecting to ADS1115: {e}")
    print("Make sure the ADS1115 is properly connected")
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

print(f"Streaming ECG data to {TARGET_IP}:{UDP_PORT}")
print(f"Sample rate: ~{1/0.01:.0f} Hz")
print("Press Ctrl+C to stop")

try:
    while True:
        # Read voltage
        voltage = chan0.voltage  # in volts
        
        # For differential mode, use:
        # voltage = chan.voltage

        # Send as binary float (4 bytes) via UDP
        message = struct.pack('f', voltage)
        sock.sendto(message, (TARGET_IP, UDP_PORT))

        # Optional: Print to console (uncomment to debug)
        # print(f"{voltage:.6f}V")

        # Adjust sleep time for desired sample rate:
        # 0.01 = ~100 Hz
        # 0.005 = ~200 Hz
        # 0.002 = ~500 Hz (recommended)
        # 0.001 = ~1000 Hz
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nStopped by user")
finally:
    sock.close()
