import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const Heatmap = ({ stats }) => {
  const chartData = stats?.zone_counts ? Object.keys(stats.zone_counts).map(zone => ({
    name: zone,
    count: stats.zone_counts[zone]
  })) : [];

  return (
    <div className="flex flex-col h-full text-white">
      <h3 className="font-label-caps text-[12px] text-white/70 mb-4 tracking-widest">ZONE ACTIVITY HEATMAP</h3>
      <div className="flex-1 relative">
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%" className="absolute inset-0">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
              <XAxis dataKey="name" stroke="rgba(255,255,255,0.5)" tick={{ fill: 'rgba(255,255,255,0.5)' }} axisLine={false} tickLine={false} />
              <YAxis stroke="rgba(255,255,255,0.5)" tick={{ fill: 'rgba(255,255,255,0.5)' }} axisLine={false} tickLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#131b2e', borderColor: 'rgba(255,255,255,0.1)', color: '#fff', borderRadius: '8px' }}
                itemStyle={{ color: '#00e3fd' }}
                cursor={{fill: 'rgba(255,255,255,0.05)'}}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.name === 'entrance' ? '#9466ff' : '#00e3fd'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-white/40 font-mono-data text-sm border border-dashed border-white/10 rounded-lg bg-white/5">
            Waiting for zone data...
          </div>
        )}
      </div>
    </div>
  );
};

export default Heatmap;
