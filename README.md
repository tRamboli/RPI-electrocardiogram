# ECG Real-Time Monitor

A real-time ECG monitoring system with web-based visualization, featuring live heart rate (BPM) calculation and adjustable peak detection.

## System Architecture

- **Raspberry Pi**: Reads ECG data from ADS1115 ADC and sends via UDP
- **Flask Backend**: Receives UDP data and streams to clients via WebSocket
- **React Frontend**: Real-time visualization with scrolling graph and BPM detection

## Prerequisites

### Windows PC Requirements
- Python 3.11+ with conda
- Node.js and npm
- Network access to Raspberry Pi

### Raspberry Pi Requirements
- Python 3.x
- ADS1115 ADC connected via I2C
- ECG electrodes connected to ADC

## Installation

### 1. Install Python Dependencies

```powershell
# Install Flask and dependencies
conda install -y flask flask-socketio flask-cors python-socketio eventlet

# Install data processing libraries
pip install matplotlib numpy scipy
```

### 2. Install Node.js Dependencies

```powershell
npm install
```

### 3. Configure Firewall

Open UDP port 5006 for incoming ECG data:

**Option 1: Run PowerShell as Administrator**
```powershell
New-NetFirewallRule -DisplayName "ECG UDP Port 5006" -Direction Inbound -Protocol UDP -LocalPort 5006 -Action Allow
```

**Option 2: Windows Defender Firewall GUI**
1. Open Windows Defender Firewall with Advanced Security
2. Click "Inbound Rules" → "New Rule"
3. Select "Port" → Next
4. Select "UDP" and enter port `5006` → Next
5. Select "Allow the connection" → Next
6. Check all profiles → Next
7. Name it "ECG UDP Port 5006" → Finish

## Configuration

### Raspberry Pi Setup

Update the server code on your Raspberry Pi:

```python
import time
import socket
import struct
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# UDP configuration
UDP_PORT = 5006
TARGET_IP = "192.168.0.168"  # Your Windows PC IP address

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Create the I2C bus and ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# CRITICAL: Set high gain for small ECG signals
ads.gain = 16  # ±0.256V range, most sensitive

# Use DIFFERENTIAL mode (measures difference between two inputs)
chan = AnalogIn(ads, ADS.P0, ADS.P1)

print(f"Streaming ECG data to {TARGET_IP}:{UDP_PORT}")

while True:
    voltage = chan.voltage
    message = struct.pack('f', voltage)
    sock.sendto(message, (TARGET_IP, UDP_PORT))
    print(f"{voltage:.6f}V")
    time.sleep(0.002)  # 500 Hz sample rate
```

**Electrode Connections:**
- **AIN0 (P0)**: Right arm electrode
- **AIN1 (P1)**: Left arm electrode
- **GND**: Right leg electrode (REQUIRED for reference)

### Find Your PC IP Address

```powershell
ipconfig | Select-String "IPv4"
```

Look for the IP on the same network as your Raspberry Pi (e.g., 192.168.0.x).

## Running the Application

### Step 1: Start Flask Backend Server

Open a terminal and run:

```powershell
python realtime_server.py
```

You should see:
```
UDP receiver listening on 0.0.0.0:5006
Starting web server on http://localhost:5001
```

### Step 2: Start React Frontend

Open a **second terminal** and run:

```powershell
npm start
```

The browser will automatically open to `http://localhost:3000`

### Step 3: Start ECG Data Streaming

On your Raspberry Pi, run the ECG server script to start sending data.

## Usage

### Web Interface Features

1. **Heart Rate (BPM)**: Displays beats per minute, calculated from last 5 heartbeats
2. **Sample Rate**: Shows data reception rate in Hz
3. **Current Voltage**: Real-time voltage reading
4. **Total Samples**: Count of received samples
5. **Status**: Connection status indicator

### Adjusting Peak Detection Threshold

Use the slider at the top to adjust the peak detection threshold:

- **Too Low**: Will detect noise as heartbeats (BPM too high)
- **Too High**: Will miss heartbeats (BPM too low or zero)
- **Optimal**: Should be just below your ECG peak voltage

**How to adjust:**
1. Watch the ECG graph and observe peak voltages
2. Slide the threshold until BPM displays correctly
3. Typical range: 0.001V - 0.005V (depends on your signal amplitude)

## Troubleshooting

### No Data Received (Total Samples = 0)

1. Check Raspberry Pi is sending to correct IP and port
2. Verify firewall port 5006 is open
3. Ensure both devices are on the same network
4. Check Raspberry Pi console for errors

### BPM Shows 0 or Incorrect Values

1. Adjust the threshold slider
2. Check electrode connections (especially ground)
3. Verify ADC gain is set to 16
4. Ensure using differential mode on ADS1115

### Graph Shows Only Noise

1. **Check electrode contact**: Use ECG electrodes with conductive gel
2. **Verify ground connection**: Right leg MUST be connected to GND
3. **Use differential mode**: `AnalogIn(ads, ADS.P0, ADS.P1)` not single-ended
4. **Set correct gain**: `ads.gain = 16` for best sensitivity
5. **Increase sample rate**: Change `time.sleep(0.002)` for 500 Hz

### Connection Issues

**Backend won't start:**
- Port 5001 in use: Change port in `realtime_server.py` and `src/App.js`
- Port 5006 in use: Change UDP_PORT in `realtime_server.py` and Raspberry Pi code

**Frontend won't connect:**
- Check Flask server is running
- Verify WebSocket connection at `http://localhost:5001`
- Check browser console for errors

## Technical Details

### Sample Rate Recommendations

- **Medical diagnostic**: 500-1000 Hz
- **Basic heart rate monitoring**: 250-360 Hz
- **Minimum acceptable**: 200 Hz

Current setup: ~500 Hz (`time.sleep(0.002)`)

### Signal Processing

- **Bandpass filter**: 0.5-40 Hz (standard ECG range)
- **DC offset removal**: Centers signal around zero
- **Peak detection**: Threshold-based with rising edge detection
- **BPM calculation**: Average of last 5 R-R intervals

### Network Protocol

- **Transport**: UDP (low latency)
- **Packet size**: 4 bytes (float32)
- **Data format**: Little-endian binary float
- **WebSocket**: Real-time client updates

## Files

- `realtime_server.py` - Flask backend with UDP receiver
- `src/App.js` - React frontend with ECG visualization
- `src/App.css` - Styling for ECG monitor interface
- `plot_ecg.py` - Standalone script for 10-second capture and filtering
- `package.json` - Node.js dependencies
- `README.md` - This file

## License

MIT License

## Support

For issues or questions, check:
1. Electrode connections and grounding
2. Network connectivity between devices
3. Firewall settings
4. ADC configuration (gain, mode)
