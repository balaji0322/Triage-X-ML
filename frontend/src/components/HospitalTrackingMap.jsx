// src/components/HospitalTrackingMap.jsx
import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './HospitalTrackingMap.css';

// Fix Leaflet default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom ambulance icon with rotation
const createAmbulanceIcon = (heading = 0) => {
  return L.divIcon({
    html: `
      <div style="transform: rotate(${heading}deg); transform-origin: center;">
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="red" stroke-width="2">
          <rect x="1" y="3" width="15" height="13" rx="2" ry="2"/>
          <path d="M16 8h5l3 3v5h-2"/>
          <circle cx="5.5" cy="18.5" r="2.5"/>
          <circle cx="18.5" cy="18.5" r="2.5"/>
          <path d="M5 10h4"/>
          <path d="M7 8v4"/>
        </svg>
      </div>
    `,
    className: 'ambulance-marker',
    iconSize: [40, 40],
    iconAnchor: [20, 20]
  });
};

const hospitalIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="blue">
      <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z"/>
      <path fill="white" d="M11 8h2v3h3v2h-3v3h-2v-3H8v-2h3V8z"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

// Component to auto-fit bounds
function AutoFitBounds({ ambulances, hospital }) {
  const map = useMap();
  
  useEffect(() => {
    const bounds = [];
    
    // Add hospital location
    if (hospital) {
      bounds.push([hospital.latitude, hospital.longitude]);
    }
    
    // Add ambulance locations
    if (ambulances && ambulances.length > 0) {
      ambulances.forEach(amb => {
        bounds.push([amb.latitude, amb.longitude]);
      });
    }
    
    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [ambulances, hospital, map]);
  
  return null;
}

function HospitalTrackingMap({ ambulances, hospitalLocation }) {
  const [mapCenter, setMapCenter] = useState([13.0827, 80.2707]); // Default: Chennai
  const [selectedAmbulance, setSelectedAmbulance] = useState(null);
  const [ambulanceTrails, setAmbulanceTrails] = useState({}); // Store trail for each ambulance

  useEffect(() => {
    if (hospitalLocation) {
      setMapCenter([hospitalLocation.latitude, hospitalLocation.longitude]);
    }
  }, [hospitalLocation]);

  // Update ambulance trails
  useEffect(() => {
    if (ambulances && ambulances.length > 0) {
      setAmbulanceTrails(prev => {
        const newTrails = { ...prev };
        
        ambulances.forEach(amb => {
          const position = [amb.latitude, amb.longitude];
          
          if (!newTrails[amb.ambulance_id]) {
            newTrails[amb.ambulance_id] = [position];
          } else {
            // Add new position to trail (keep last 20 positions)
            const trail = [...newTrails[amb.ambulance_id], position];
            newTrails[amb.ambulance_id] = trail.slice(-20);
          }
        });
        
        return newTrails;
      });
    }
  }, [ambulances]);

  return (
    <div className="hospital-tracking-map-container">
      <MapContainer
        center={mapCenter}
        zoom={12}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <AutoFitBounds ambulances={ambulances} hospital={hospitalLocation} />
        
        {/* Hospital marker */}
        {hospitalLocation && (
          <Marker
            position={[hospitalLocation.latitude, hospitalLocation.longitude]}
            icon={hospitalIcon}
          >
            <Popup>
              <div className="map-popup">
                <h3>🏥 Your Hospital</h3>
                <p>{hospitalLocation.name}</p>
                <p>Lat: {hospitalLocation.latitude.toFixed(4)}</p>
                <p>Lng: {hospitalLocation.longitude.toFixed(4)}</p>
              </div>
            </Popup>
          </Marker>
        )}
        
        {/* Ambulance markers with trails */}
        {ambulances && ambulances.map((ambulance) => {
          const trail = ambulanceTrails[ambulance.ambulance_id] || [];
          
          return (
            <React.Fragment key={ambulance.ambulance_id}>
              {/* Trail line */}
              {trail.length > 1 && (
                <Polyline
                  positions={trail}
                  pathOptions={{
                    color: '#ef4444',
                    weight: 3,
                    opacity: 0.6,
                    dashArray: '5, 10'
                  }}
                />
              )}
              
              {/* Ambulance marker */}
              <Marker
                position={[ambulance.latitude, ambulance.longitude]}
                icon={createAmbulanceIcon(ambulance.heading || 0)}
                eventHandlers={{
                  click: () => setSelectedAmbulance(ambulance)
                }}
              >
                <Popup>
                  <div className="map-popup">
                    <h3>🚑 {ambulance.ambulance_number}</h3>
                    <p><strong>Driver:</strong> {ambulance.driver_name}</p>
                    <p><strong>Speed:</strong> {ambulance.speed || 0} km/h</p>
                    <p><strong>Location:</strong></p>
                    <p>Lat: {ambulance.latitude.toFixed(4)}</p>
                    <p>Lng: {ambulance.longitude.toFixed(4)}</p>
                    <p className="timestamp">
                      Last update: {new Date(ambulance.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
      </MapContainer>
      
      {/* Active ambulances panel */}
      <div className="active-ambulances-panel">
        <h3>🚑 Active Ambulances ({ambulances ? ambulances.length : 0})</h3>
        <div className="ambulance-list">
          {ambulances && ambulances.length > 0 ? (
            ambulances.map(amb => (
              <div
                key={amb.ambulance_id}
                className={`ambulance-item ${selectedAmbulance?.ambulance_id === amb.ambulance_id ? 'selected' : ''}`}
                onClick={() => setSelectedAmbulance(amb)}
              >
                <div className="ambulance-info">
                  <span className="ambulance-number">{amb.ambulance_number}</span>
                  <span className="ambulance-speed">{amb.speed || 0} km/h</span>
                </div>
                <div className="ambulance-driver">{amb.driver_name}</div>
                <div className="ambulance-time">
                  {new Date(amb.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))
          ) : (
            <div className="no-ambulances">No active ambulances</div>
          )}
        </div>
      </div>
      
      {/* Map legend */}
      <div className="map-legend">
        <div className="legend-item">
          <span className="legend-icon">🚑</span>
          <span>Ambulance</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">🏥</span>
          <span>Hospital</span>
        </div>
        <div className="legend-item">
          <div className="legend-line"></div>
          <span>Trail</span>
        </div>
      </div>
    </div>
  );
}

export default HospitalTrackingMap;
