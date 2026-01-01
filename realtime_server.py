import socket
import struct
import threading
import json
from flask import Flask, render_template, Response, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from collections import deque
import time
import os

# Serve React build folder
app = Flask(__name__, static_folder='build', static_url_path='')
app.config['SECRET_KEY'] = 'ecg_secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# UDP configuration
UDP_IP = "0.0.0.0"
UDP_PORT = 5006

# Data storage - 10 second window
MAX_POINTS = 5000  # Adjust based on sample rate
ecg_data = {
    'timestamps': deque(maxlen=MAX_POINTS),
    'voltages': deque(maxlen=MAX_POINTS)
}
start_time = None
data_lock = threading.Lock()

def udp_receiver():
    """Background thread to receive UDP data"""
    global start_time
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"UDP receiver listening on {UDP_IP}:{UDP_PORT}")
    
    start_time = time.time()
    
    while True:
        try:
            data, addr = sock.recvfrom(4)
            voltage = struct.unpack('f', data)[0]
            current_time = time.time() - start_time
            
            with data_lock:
                ecg_data['timestamps'].append(current_time)
                ecg_data['voltages'].append(voltage)
            
            # Emit to all connected clients
            socketio.emit('ecg_data', {
                'time': current_time,
                'voltage': voltage
            })
            
        except Exception as e:
            print(f"Error receiving data: {e}")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/data')
def get_data():
    """Get current buffered data"""
    with data_lock:
        return jsonify({
            'timestamps': list(ecg_data['timestamps']),
            'voltages': list(ecg_data['voltages'])
        })

@app.errorhandler(404)
def not_found(e):
    # Serve index.html for React Router
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Start UDP receiver in background thread
    receiver_thread = threading.Thread(target=udp_receiver, daemon=True)
    receiver_thread.start()
    
    print("Starting web server on http://localhost:5001")
    print("UDP receiver listening on port 5005")
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)
