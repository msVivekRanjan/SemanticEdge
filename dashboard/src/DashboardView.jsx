import React, { useState, useEffect } from 'react';
import axios from 'axios';
import EventFeed from './EventFeed';
import Heatmap from './Heatmap';

function DashboardView({ onLogout }) {
  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({
    zone_counts: {},
    unique_persons: 0,
    total_events: 0
  });

  useEffect(() => {
    let ws;
    let reconnectTimer;

    const connect = () => {
      ws = new WebSocket('ws://localhost:8000/ws');

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setEvents((prev) => [data, ...prev].slice(0, 50));
        } catch (err) {
          console.error('Failed to parse websocket message', err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        reconnectTimer = setTimeout(connect, 3000);
      };
      
      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        ws.close();
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      if (ws) {
        ws.close();
      }
    };
  }, []);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('http://localhost:8000/stats');
        setStats(response.data);
      } catch (err) {
        console.error('Failed to fetch stats', err);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 3000);
    return () => clearInterval(interval);
  }, []);

  const activeZones = Object.keys(stats?.zone_counts || {}).length;

  return (
    <div className="min-h-screen flex flex-col bg-[#0b101e] font-body-md text-white selection:bg-secondary-container selection:text-on-secondary-container">
      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 bg-[#0b101e]/80 backdrop-blur-xl border-b border-white/10">
        <div className="flex justify-between items-center px-6 md:px-12 py-4 max-w-[1600px] mx-auto">
          <div className="font-headline-md text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <span className="material-symbols-outlined text-secondary">hub</span>
            SemanticEdge <span className="text-secondary font-light">Analytics</span>
          </div>
          <div className="flex items-center gap-6">
            <div className="hidden sm:flex items-center gap-2 bg-white/5 px-4 py-2 rounded-full border border-white/10">
              <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-[#00ff88] animate-pulse shadow-[0_0_10px_#00ff88]' : 'bg-error'}`}></span>
              <span className="font-label-caps text-[10px] text-white/70 tracking-widest">
                {isConnected ? 'SECURE UPLINK ACTIVE' : 'RECONNECTING...'}
              </span>
            </div>
            <button className="text-white/70 hover:text-white transition-colors duration-300 font-label-caps text-[12px] tracking-wider" onClick={onLogout}>
              LOGOUT
            </button>
          </div>
        </div>
      </nav>

      <main className="flex-1 pt-28 pb-12 px-6 md:px-12 max-w-[1600px] mx-auto w-full flex flex-col">
        {/* Header */}
        <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="font-display-lg text-4xl mb-2 font-bold bg-gradient-to-r from-white to-white/50 bg-clip-text text-transparent">Global Insights Terminal</h1>
            <p className="text-white/50 max-w-2xl text-sm">Real-time metadata traffic aggregation across all edge nodes. No raw video is processed or stored in this environment.</p>
          </div>
          <div className="flex gap-2">
            <span className="px-3 py-1 rounded-full bg-white/5 text-white/60 text-[10px] font-label-caps border border-white/10 flex items-center gap-1">
              <span className="material-symbols-outlined text-[12px]">lock</span> ENCRYPTED
            </span>
            <span className="px-3 py-1 rounded-full bg-secondary/10 text-secondary border border-secondary/20 text-[10px] font-label-caps flex items-center gap-1">
              <span className="material-symbols-outlined text-[12px]">speed</span> 5G SLICE
            </span>
          </div>
        </div>

        {/* Pulse Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-[#131b2e]/50 backdrop-blur-md border border-white/5 p-6 rounded-2xl relative overflow-hidden group hover:border-white/20 transition-all duration-300">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <span className="material-symbols-outlined text-4xl">data_usage</span>
            </div>
            <div className="text-[10px] font-label-caps text-white/40 mb-2 tracking-widest">TOTAL EVENTS PROCESSED</div>
            <div className="text-4xl font-bold font-mono-data text-white flex items-baseline gap-2">
              {stats.total_events} <span className="text-sm font-body-md text-[#00ff88]">+12%</span>
            </div>
          </div>
          <div className="bg-[#131b2e]/50 backdrop-blur-md border border-white/5 p-6 rounded-2xl relative overflow-hidden group hover:border-white/20 transition-all duration-300">
             <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <span className="material-symbols-outlined text-4xl">person_search</span>
            </div>
            <div className="text-[10px] font-label-caps text-white/40 mb-2 tracking-widest">UNIQUE PERSONS DETECTED</div>
            <div className="text-4xl font-bold font-mono-data text-[#00e3fd]">{stats.unique_persons}</div>
          </div>
          <div className="bg-[#131b2e]/50 backdrop-blur-md border border-white/5 p-6 rounded-2xl relative overflow-hidden group hover:border-white/20 transition-all duration-300">
             <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <span className="material-symbols-outlined text-4xl">share_location</span>
            </div>
            <div className="text-[10px] font-label-caps text-white/40 mb-2 tracking-widest">ACTIVE SURVEILLANCE ZONES</div>
            <div className="text-4xl font-bold font-mono-data text-[#9466ff]">{activeZones}</div>
          </div>
          <div className="bg-[#131b2e]/50 backdrop-blur-md border border-white/5 p-6 rounded-2xl relative overflow-hidden group hover:border-white/20 transition-all duration-300">
             <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <span className="material-symbols-outlined text-4xl">dns</span>
            </div>
            <div className="text-[10px] font-label-caps text-white/40 mb-2 tracking-widest">MEC NODE STATUS</div>
            <div className={`text-4xl font-bold font-mono-data ${isConnected ? 'text-[#00ff88]' : 'text-error'}`}>
              {isConnected ? 'ONLINE' : 'OFFLINE'}
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 flex-1 min-h-0">
          
          {/* Left: Live Event Feed */}
          <div className="bg-[#131b2e]/50 backdrop-blur-md border border-white/5 rounded-3xl p-6 md:p-8 flex flex-col h-[500px] lg:h-auto">
            <div className="flex items-center justify-between mb-6 shrink-0 border-b border-white/5 pb-4">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-secondary">list_alt</span>
                <h3 className="font-headline-md text-xl font-medium tracking-wide">Live Metadata Stream</h3>
              </div>
              <div className="flex items-center gap-2 bg-white/5 px-3 py-1 rounded-full">
                <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-[#00ff88] animate-pulse' : 'bg-error'}`}></span>
                <span className="text-[10px] font-label-caps text-white/60 tracking-wider">REAL-TIME</span>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto pr-4 custom-scrollbar relative">
              <EventFeed events={events} />
            </div>
          </div>

          {/* Right: Heatmap Area */}
          <div className="bg-[#131b2e]/50 backdrop-blur-md border border-white/5 rounded-3xl p-6 md:p-8 flex flex-col h-[500px] lg:h-auto">
             <div className="flex items-center justify-between mb-6 shrink-0 border-b border-white/5 pb-4">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-[#9466ff]">map</span>
                <h3 className="font-headline-md text-xl font-medium tracking-wide">Spatial Activity Analysis</h3>
              </div>
              <button className="text-white/40 hover:text-white transition-colors">
                <span className="material-symbols-outlined">more_horiz</span>
              </button>
            </div>
            <div className="flex-1 min-h-0 relative">
              <Heatmap stats={stats} />
            </div>
          </div>

        </div>
      </main>

      {/* Subtle Background Effects */}
      <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-secondary/10 blur-[120px] rounded-full mix-blend-screen"></div>
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-[#9466ff]/10 blur-[120px] rounded-full mix-blend-screen"></div>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.02);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
        .event-item {
          background: rgba(255, 255, 255, 0.03) !important;
          border: 1px solid rgba(255, 255, 255, 0.05) !important;
          color: white !important;
        }
        .event-header {
          color: rgba(255, 255, 255, 0.5) !important;
        }
        .object-tag {
          background: rgba(0, 227, 253, 0.1) !important;
          color: #00e3fd !important;
          border: 1px solid rgba(0, 227, 253, 0.2);
        }
      `}</style>
    </div>
  );
}

export default DashboardView;
