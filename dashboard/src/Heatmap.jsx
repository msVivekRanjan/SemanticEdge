import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const Heatmap = () => {
  const [stats, setStats] = useState({
    zone_counts: {},
    unique_persons: 0,
    total_events: 0
  });

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

  const chartData = Object.keys(stats.zone_counts).map(zone => ({
    name: zone,
    count: stats.zone_counts[zone]
  }));

  const activeZones = Object.keys(stats.zone_counts).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div className="stats-grid">
        <div className="stat-box">
          <div className="stat-label">Total Events</div>
          <div className="stat-value">{stats.total_events}</div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Persons Detected</div>
          <div className="stat-value">{stats.unique_persons}</div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Active Zones</div>
          <div className="stat-value">{activeZones}</div>
        </div>
      </div>

      <div className="chart-container">
        <h3>Zone Activity Heatmap</h3>
        <div style={{ flex: 1, minHeight: 0 }}>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2e3d" vertical={false} />
                <XAxis dataKey="name" stroke="#8b92a5" tick={{ fill: '#8b92a5' }} axisLine={false} tickLine={false} />
                <YAxis stroke="#8b92a5" tick={{ fill: '#8b92a5' }} axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1a1d27', borderColor: '#2a2e3d', color: '#fff' }}
                  itemStyle={{ color: '#00ff88' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.name === 'entrance' ? '#00ff88' : '#00d2ff'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
              No data available
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Heatmap;
