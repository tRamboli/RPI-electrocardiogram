#!/usr/bin/env python3
"""
ECG Data Plotter for Raspberry Pi
Reads ECG data from file and creates visualizations
"""

import matplotlib.pyplot as plt
import numpy as np

# Read data from file
data = []
with open('ecg_data.txt', 'r') as f:
    for line in f:
        # Skip comment lines
        if line.startswith('#'):
            continue
        # Parse CSV: sample_number,time(s),voltage(V)
        parts = line.strip().split(',')
        if len(parts) == 3:
            sample_num = int(parts[0])
            time = float(parts[1])
            voltage = float(parts[2])
            data.append([sample_num, time, voltage])

# Convert to numpy arrays
data = np.array(data)
sample_numbers = data[:, 0]
time = data[:, 1]
voltage = data[:, 2]

# Create figure with subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Plot 1: Full ECG trace
ax1.plot(time, voltage, linewidth=0.5, color='blue')
ax1.set_xlabel('Time (seconds)', fontsize=12)
ax1.set_ylabel('Voltage (V)', fontsize=12)
ax1.set_title('ECG Signal - Full Recording (10 seconds)', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_xlim([time[0], time[-1]])

# Plot 2: Zoomed view (first 2 seconds)
zoom_end = 2.0  # seconds
zoom_indices = time <= zoom_end
ax2.plot(time[zoom_indices], voltage[zoom_indices], linewidth=1, color='red')
ax2.set_xlabel('Time (seconds)', fontsize=12)
ax2.set_ylabel('Voltage (V)', fontsize=12)
ax2.set_title('ECG Signal - Zoomed View (First 2 seconds)', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_xlim([0, zoom_end])

# Add statistics
mean_voltage = np.mean(voltage)
std_voltage = np.std(voltage)
min_voltage = np.min(voltage)
max_voltage = np.max(voltage)

stats_text = f'Statistics:\nMean: {mean_voltage:.6f} V\nStd Dev: {std_voltage:.6f} V\nMin: {min_voltage:.6f} V\nMax: {max_voltage:.6f} V\nSamples: {len(voltage)}'

fig.text(0.02, 0.02, stats_text, fontsize=10, family='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout(rect=[0, 0.08, 1, 1])
plt.savefig('ecg_plot.png', dpi=150, bbox_inches='tight')
print(f"Plot saved to: ecg_plot.png")
print(f"\nStatistics:")
print(f"  Total samples: {len(voltage)}")
print(f"  Duration: {time[-1]:.3f} seconds")
print(f"  Sample rate: {len(voltage)/time[-1]:.2f} Hz")
print(f"  Mean voltage: {mean_voltage:.6f} V")
print(f"  Std deviation: {std_voltage:.6f} V")
print(f"  Min voltage: {min_voltage:.6f} V")
print(f"  Max voltage: {max_voltage:.6f} V")

plt.show()
