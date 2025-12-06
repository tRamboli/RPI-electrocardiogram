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
TARGET_IP = "192.168.0.168"  # Change to your Windows PC IP address

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Optional: Set gain for better sensitivity
# ads.gain = 16  # ±0.256V range (most sensitive for small ECG signals)
# ads.gain = 8   # ±0.512V range
# ads.gain = 4   # ±1.024V range (default)
# ads.gain = 2   # ±2.048V range
# ads.gain = 1   # ±4.096V range

# Create single-ended input on channel 0
chan0 = AnalogIn(ads, 0)

# For differential mode (recommended for ECG):
# Uncomment the following line and comment out the chan0 line above
# chan = AnalogIn(ads, ADS.P0, ADS.P1)

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
