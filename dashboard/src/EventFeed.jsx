import React from 'react';

const EventFeed = ({ events }) => {
  if (!events || events.length === 0) {
    return (
      <div className="card" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span style={{ color: 'var(--text-muted)' }}>Waiting for events...</span>
      </div>
    );
  }

  return (
    <div className="event-list">
      {events.map((event, index) => {
        const timeStr = event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : 'Unknown Time';
        const zone = event.zone || 'unknown';
        
        return (
          <div key={event._id || index} className="event-card">
            <div className="event-header">
              <span>{event.cam_id || 'CAM_01'}</span>
              <span>{timeStr}</span>
            </div>
            
            <div style={{ marginBottom: '10px' }}>
              <span className={`badge ${zone}`}>{zone}</span>
            </div>
            
            <div className="event-body">
              {event.objects && event.objects.length > 0 ? (
                event.objects.map((obj, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
                    <span style={{ textTransform: 'capitalize' }}>👤 {obj.type}</span>
                    <span style={{ color: 'var(--text-muted)' }}>{(obj.confidence * 100).toFixed(0)}%</span>
                  </div>
                ))
              ) : (
                <span style={{ color: 'var(--text-muted)' }}>No objects tracked</span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default EventFeed;
