#!/usr/bin/env python3
"""
ECG Data Recorder Simulator
Generates simulated ECG data and saves to file for testing with rpi_plot_ecg.py
Use this for testing without actual hardware
"""

import time
import math
import random

# Recording configuration
OUTPUT_FILE = "ecg_data.txt"
DURATION = 10  # seconds to record
SAMPLE_RATE = 0.01  # 0.01 = ~100 Hz

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

print(f"Recording simulated ECG data to {OUTPUT_FILE}")
print(f"Duration: {DURATION} seconds")
print(f"Sample rate: ~{1/SAMPLE_RATE:.0f} Hz")
print("Press Ctrl+C to stop early")

try:
    with open(OUTPUT_FILE, 'w') as f:
        # Write header
        f.write("# ECG Data Recording (Simulated)\n")
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
            
            # Generate simulated voltage
            voltage = generate_ecg_sample(elapsed_time)
            
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
