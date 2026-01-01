import time
import board
import busio
import numpy as np
import matplotlib.pyplot as plt
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# =====================
# CONFIGURATION
# =====================
FS = 500                  # Sampling rate in Hz
DURATION = 5              # Seconds to record
CHANNEL = 0               # ADS1115 channel 0 → A0

# =====================
# I2C + ADS1115 SETUP
# =====================
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
# ads.gain = 1               # ±4.096V
# ads.data_rate = FS         # Data rate in SPS

chan = AnalogIn(ads, CHANNEL)

# =====================
# DATA ACQUISITION
# =====================
num_samples = FS * DURATION
ecg_data = []

print(f"Recording raw ECG for {DURATION} seconds at {FS} Hz...")

while len(ecg_data) < num_samples:
    v = chan.voltage
    ecg_data.append(v)
    time.sleep(1 / FS)

print("Recording complete.")

# =====================
# PLOT AND SAVE TO PNG
# =====================
plt.figure(figsize=(10, 4))
plt.plot(ecg_data, lw=1)
plt.title(f"Raw ECG ({DURATION}s, {FS} Hz)")
plt.xlabel("Sample Number")
plt.ylabel("Voltage (V)")
plt.grid(True)
plt.tight_layout()

plt.savefig("ecg_raw_5s.png", dpi=300)
plt.show()

print("ECG plot saved as 'ecg_raw_5s.png'")