#!/usr/bin/env python3
"""
ECG UDP Simulator
Generates simulated ECG data and sends via UDP to the realtime server
"""

import time
import socket
import struct
import math
import random

# UDP configuration
UDP_PORT = 5006
TARGET_IP = "127.0.0.1"  # localhost

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def generate_ecg_sample(t):
    """Generate a simulated ECG waveform"""
    # Simple simulated ECG with P, QRS, and T waves
    heart_rate = 75  # BPM
    frequency = heart_rate / 60.0  # Hz
    
    # Baseline with slight drift
    baseline = 1.5 + 0.1 * math.sin(0.1 * t)
    
    # ECG waveform (simplified)
    phase = (t * frequency) % 1.0
    
    if phase < 0.15:  # P wave
        signal = 0.1 * math.sin(phase / 0.15 * math.pi)
    elif phase < 0.25:  # PR segment
        signal = 0
    elif phase < 0.35:  # QRS complex
        signal = 0.8 * math.sin((phase - 0.25) / 0.1 * math.pi)
    elif phase < 0.45:  # ST segment
        signal = 0
    elif phase < 0.65:  # T wave
        signal = 0.2 * math.sin((phase - 0.45) / 0.2 * math.pi)
    else:  # Rest
        signal = 0
    
    # Add small noise
    noise = random.gauss(0, 0.01)
    
    return baseline + signal + noise

print(f"Streaming simulated ECG data to {TARGET_IP}:{UDP_PORT}")
print(f"Sample rate: ~{1/0.01:.0f} Hz")
print("Press Ctrl+C to stop")

try:
    start_time = time.time()
    sample_count = 0
    
    while True:
        elapsed = time.time() - start_time
        
        # Generate voltage
        voltage = generate_ecg_sample(elapsed)
        
        # Send as binary float (4 bytes) via UDP
        message = struct.pack('f', voltage)
        sock.sendto(message, (TARGET_IP, UDP_PORT))
        
        sample_count += 1
        
        # Print progress
        if sample_count % 100 == 0:
            print(f"Sent {sample_count} samples ({elapsed:.1f}s)")
        
        # Adjust sleep time for desired sample rate:
        # 0.01 = ~100 Hz
        # 0.005 = ~200 Hz
        # 0.002 = ~500 Hz
        time.sleep(0.01)

except KeyboardInterrupt:
    print(f"\nStopped. Sent {sample_count} samples")
finally:
    sock.close()
