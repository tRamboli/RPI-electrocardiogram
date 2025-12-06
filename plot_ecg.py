import socket
import struct
import time
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from scipy import signal

# UDP configuration
UDP_IP = "0.0.0.0"  # Listen on all network interfaces
UDP_PORT = 5005

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for ECG data on {UDP_IP}:{UDP_PORT}")
print("Recording for 10 seconds...")

# Data storage
voltages = []
timestamps = []
start_time = time.time()

try:
    while True:
        # Receive data (4 bytes for float)
        data, addr = sock.recvfrom(4)
        
        # Unpack binary float
        voltage = struct.unpack('f', data)[0]
        
        # Store data
        current_time = time.time() - start_time
        voltages.append(voltage)
        timestamps.append(current_time)
        
        print(f"{current_time:.2f}s - {voltage:.3f}V")
        
        # Stop after 10 seconds
        if current_time >= 10.0:
            break

except KeyboardInterrupt:
    print("\nStopped by user")

finally:
    sock.close()
    
    if len(voltages) == 0:
        print("No data received!")
        exit()
    
    # Convert to numpy arrays
    voltages = np.array(voltages)
    timestamps = np.array(timestamps)
    
    # Calculate sample rate
    sample_rate = len(voltages) / timestamps[-1]
    print(f"\nTotal samples: {len(voltages)}")
    print(f"Sample rate: ~{sample_rate:.1f} Hz")
    print(f"Voltage range: {voltages.min():.4f}V to {voltages.max():.4f}V")
    print(f"Voltage mean: {voltages.mean():.4f}V")
    print(f"Voltage std dev: {voltages.std():.4f}V")
    
    # Remove DC offset
    voltages_centered = voltages - np.mean(voltages)
    
    # Apply bandpass filter (0.5-40 Hz for ECG)
    nyquist = sample_rate / 2
    low = 0.5 / nyquist
    high = min(40.0, nyquist * 0.9) / nyquist  # Don't exceed Nyquist
    
    voltages_filtered = voltages_centered
    if high < 1.0 and low < high:
        try:
            b, a = signal.butter(3, [low, high], btype='band')
            voltages_filtered = signal.filtfilt(b, a, voltages_centered)
        except Exception as e:
            print(f"Filter warning: {e}")
            voltages_filtered = voltages_centered
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # Plot 1: Raw signal
    axes[0].plot(timestamps, voltages, linewidth=0.5, color='blue')
    axes[0].set_ylabel('Voltage (V)')
    axes[0].set_title('Raw ECG Signal')
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Centered signal
    axes[1].plot(timestamps, voltages_centered, linewidth=0.6, color='green')
    axes[1].set_ylabel('Voltage (V)')
    axes[1].set_title('DC Offset Removed')
    axes[1].grid(True, alpha=0.3)
    
    # Plot 3: Filtered signal
    axes[2].plot(timestamps, voltages_filtered, linewidth=0.8, color='red')
    axes[2].set_xlabel('Time (seconds)')
    axes[2].set_ylabel('Voltage (V)')
    axes[2].set_title(f'Filtered ECG Signal ({low*nyquist:.1f}-{high*nyquist:.1f} Hz Bandpass)')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save image
    filename = f"ecg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(filename, dpi=300)
    print(f"\nPlot saved as: {filename}")
