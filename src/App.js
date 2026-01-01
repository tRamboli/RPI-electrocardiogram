import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
  const [ecgData, setEcgData] = useState([]);
  const [stats, setStats] = useState({
    sampleRate: 0,
    currentVoltage: 0,
    totalSamples: 0,
    bpm: 0,
    connected: false
  });
  const [threshold, setThreshold] = useState(0.002);
  
  const socketRef = useRef(null);
  const sampleCounterRef = useRef(0);
  const lastUpdateRef = useRef(Date.now());
  const totalSamplesRef = useRef(0);
  const peakTimesRef = useRef([]);
  const lastVoltageRef = useRef(0);
  
  const WINDOW_SIZE = 10; // seconds
  const MAX_POINTS = 5000;

  useEffect(() => {
    // Connect to Socket.IO server - use window.location.hostname to work across network
    const serverUrl = `http://${window.location.hostname}:5001`;
    socketRef.current = io(serverUrl);
    
    socketRef.current.on('connect', () => {
      console.log('Connected to server');
      setStats(prev => ({ ...prev, connected: true }));
    });
    
    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from server');
      setStats(prev => ({ ...prev, connected: false }));
    });
    
    // Load initial data
    fetch(`${serverUrl}/data`)
      .then(response => response.json())
      .then(data => {
        const initialData = data.timestamps.map((time, index) => ({
          time: time,
          voltage: data.voltages[index]
        }));
        setEcgData(initialData);
      })
      .catch(err => console.error('Error loading initial data:', err));
    
    // Listen for real-time ECG data
    socketRef.current.on('ecg_data', (data) => {
      totalSamplesRef.current++;
      sampleCounterRef.current++;
      
      // Detect peaks for BPM calculation
      if (data.voltage > threshold && lastVoltageRef.current <= threshold) {
        // Peak detected (rising edge crossing threshold)
        peakTimesRef.current.push(data.time);
        
        // Keep only last 5 peaks
        if (peakTimesRef.current.length > 5) {
          peakTimesRef.current.shift();
        }
      }
      lastVoltageRef.current = data.voltage;
      
      setEcgData(prev => {
        const newData = [...prev, { time: data.time, voltage: data.voltage }];
        
        // Keep only last 10 seconds
        const filtered = newData.filter(point => data.time - point.time <= WINDOW_SIZE);
        
        // Limit total points
        if (filtered.length > MAX_POINTS) {
          return filtered.slice(-MAX_POINTS);
        }
        return filtered;
      });
      
      // Update stats
      const now = Date.now();
      if (now - lastUpdateRef.current >= 1000) {
        // Calculate BPM from last 5 peaks
        let bpm = 0;
        if (peakTimesRef.current.length >= 2) {
          const intervals = [];
          for (let i = 1; i < peakTimesRef.current.length; i++) {
            intervals.push(peakTimesRef.current[i] - peakTimesRef.current[i - 1]);
          }
          const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
          bpm = Math.round(60 / avgInterval);
        }
        
        setStats(prev => ({
          ...prev,
          sampleRate: sampleCounterRef.current,
          currentVoltage: data.voltage,
          totalSamples: totalSamplesRef.current,
          bpm: bpm
        }));
        sampleCounterRef.current = 0;
        lastUpdateRef.current = now;
      } else {
        setStats(prev => ({
          ...prev,
          currentVoltage: data.voltage,
          totalSamples: totalSamplesRef.current
        }));
      }
    });
    
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [threshold]);
  
  // Calculate domain for x-axis (always show last 10 seconds)
  const xDomain = ecgData.length > 0 
    ? [Math.max(0, ecgData[ecgData.length - 1].time - WINDOW_SIZE), ecgData[ecgData.length - 1].time]
    : [0, WINDOW_SIZE];

  return (
    <div className="App">
      <header className="header">
        <h1>🫀 Real-Time ECG Monitor</h1>
      </header>
      
      <div className="controls-container">
        <div className="control-box">
          <label htmlFor="threshold-slider">
            <span className="control-label">Peak Detection Threshold</span>
            <span className="control-value">{threshold.toFixed(4)} V</span>
          </label>
          <input
            id="threshold-slider"
            type="range"
            min="0"
            max="0.02"
            step="0.0001"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="threshold-slider"
          />
        </div>
      </div>

      <div className="stats-container">
        <div className="stat-box">
          <div className="stat-label">Heart Rate</div>
          <div className="stat-value" style={{ fontSize: '2.2rem', color: '#ff3366' }}>
            {stats.bpm > 0 ? `${stats.bpm} BPM` : '-- BPM'}
          </div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Sample Rate</div>
          <div className="stat-value">{stats.sampleRate} Hz</div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Current Voltage</div>
          <div className="stat-value">{stats.currentVoltage.toFixed(4)} V</div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Total Samples</div>
          <div className="stat-value">{stats.totalSamples}</div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Status</div>
          <div className={`stat-value ${stats.connected ? 'connected' : 'disconnected'}`}>
            {stats.connected ? '✓ Connected' : '✗ Disconnected'}
          </div>
        </div>
      </div>
      
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={500}>
          <LineChart data={ecgData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="time" 
              stroke="#00ff00"
              domain={xDomain}
              type="number"
              label={{ value: 'Time (seconds)', position: 'insideBottom', offset: -10, fill: '#00ff00' }}
            />
            <YAxis 
              stroke="#00ff00"
              label={{ value: 'Voltage (V)', angle: -90, position: 'insideLeft', fill: '#00ff00' }}
            />
            <Line 
              type="monotone" 
              dataKey="voltage" 
              stroke="#00ff00" 
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default App;
