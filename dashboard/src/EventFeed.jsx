import React from 'react';

const EventFeed = ({ events }) => {
  if (!events || events.length === 0) {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span className="mono-data" style={{ color: 'var(--on-surface-variant)' }}>Waiting for real-time events...</span>
      </div>
    );
  }

  return (
    <div className="event-feed">
      {events.map((event, index) => {
        const timeStr = event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : 'Unknown Time';
        
        return (
          <div key={event._id || index} className="event-item">
            <div className="event-header label-caps">
              <span>{event.cam_id || 'CAM_01'}</span>
              <span>{timeStr}</span>
            </div>
            
            <div className="event-objects">
              {event.objects && event.objects.length > 0 ? (
                event.objects.map((obj, i) => (
                  <span key={i} className="object-tag">
                    {obj.type} {(obj.confidence * 100).toFixed(0)}%
                  </span>
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
