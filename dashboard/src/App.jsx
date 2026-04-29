import React, { useState, useEffect } from 'react';
import EventFeed from './EventFeed';
import Heatmap from './Heatmap';
import { io } from 'socket.io-client';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const socket = io('ws://localhost:8000/ws', {
      transports: ['websocket']
    });

    socket.on('connect', () => {
      setIsConnected(true);
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
    });

    socket.on('message', (data) => {
      try {
        const event = typeof data === 'string' ? JSON.parse(data) : data;
        setEvents((prev) => [event, ...prev].slice(0, 50));
      } catch (err) {
        console.error('Failed to parse websocket message', err);
      }
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div className="dashboard-container">
      <header className="header">
        <h1>SemanticEdge 5G</h1>
        <div className="connection-status">
          <span>{isConnected ? 'Connected' : 'Connecting...'}</span>
          <div className={`dot ${isConnected ? 'connected' : 'disconnected'}`}></div>
        </div>
      </header>
      
      <div className="content">
        <div className="column">
          <EventFeed events={events} />
        </div>
        <div className="column">
          <Heatmap />
        </div>
      </div>
    </div>
  );
}

export default App;
