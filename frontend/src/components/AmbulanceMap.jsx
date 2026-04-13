// src/components/AmbulanceMap.jsx
import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './AmbulanceMap.css';

// Fix Leaflet default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom icons
const ambulanceIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="red" stroke-width="2">
      <rect x="1" y="3" width="15" height="13" rx="2" ry="2"/>
      <path d="M16 8h5l3 3v5h-2"/>
      <circle cx="5.5" cy="18.5" r="2.5"/>
      <circle cx="18.5" cy="18.5" r="2.5"/>
      <path d="M5 10h4"/>
      <path d="M7 8v4"/>
    </svg>
  `),
  iconSize: [40, 40],
  iconAnchor: [20, 40],
  popupAnchor: [0, -40]
});

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

const recommendedHospitalIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="green">
      <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z"/>
      <path fill="white" d="M11 8h2v3h3v2h-3v3h-2v-3H8v-2h3V8z"/>
      <circle cx="12" cy="12" r="10" fill="none" stroke="gold" stroke-width="2"/>
    </svg>
  `),
  iconSize: [40, 40],
  iconAnchor: [20, 40],
  popupAnchor: [0, -40]
});

// Component to recenter map when location changes
function MapRecenter({ center }) {
  const map = useMap();
  
  useEffect(() => {
    if (center) {
      map.setView(center, map.getZoom());
    }
  }, [center, map]);
  
  return null;
}

function AmbulanceMap({ currentLocation, hospitals, recommendedHospital }) {
  const [mapCenter, setMapCenter] = useState([13.0827, 80.2707]); // Default: Chennai
  const [zoom, setZoom] = useState(13);

  useEffect(() => {
    if (currentLocation) {
      setMapCenter([currentLocation.latitude, currentLocation.longitude]);
    }
  }, [currentLocation]);

  return (
    <div className="ambulance-map-container">
      <MapContainer
        center={mapCenter}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapRecenter center={mapCenter} />
        
        {/* Ambulance marker */}
        {currentLocation && (
          <>
            <Marker
              position={[currentLocation.latitude, currentLocation.longitude]}
              icon={ambulanceIcon}
            >
              <Popup>
                <div className="map-popup">
                  <h3>🚑 Your Location</h3>
                  <p>Lat: {currentLocation.latitude.toFixed(4)}</p>
                  <p>Lng: {currentLocation.longitude.toFixed(4)}</p>
                </div>
              </Popup>
            </Marker>
            
            {/* Radius circle around ambulance */}
            <Circle
              center={[currentLocation.latitude, currentLocation.longitude]}
              radius={5000} // 5km radius
              pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.1 }}
            />
          </>
        )}
        
        {/* Hospital markers */}
        {hospitals && hospitals.map((hospital) => {
          const isRecommended = recommendedHospital && 
                                hospital.hospital_id === recommendedHospital.hospital_id;
          
          return (
            <Marker
              key={hospital.hospital_id}
              position={[hospital.latitude, hospital.longitude]}
              icon={isRecommended ? recommendedHospitalIcon : hospitalIcon}
            >
              <Popup>
                <div className="map-popup">
                  {isRecommended && <div className="recommended-badge">⭐ RECOMMENDED</div>}
                  <h3>🏥 {hospital.hospital_name}</h3>
                  <p><strong>Distance:</strong> {hospital.distance_km} km</p>
                  <p><strong>Available Beds:</strong> {hospital.available_beds}</p>
                  <p><strong>Current Load:</strong> {hospital.current_load}</p>
                  <p><strong>Score:</strong> {hospital.score}</p>
                  <p className="hospital-address">{hospital.address}</p>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
      
      {/* Map legend */}
      <div className="map-legend">
        <div className="legend-item">
          <span className="legend-icon ambulance">🚑</span>
          <span>Your Location</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon hospital">🏥</span>
          <span>Hospital</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon recommended">⭐</span>
          <span>Recommended</span>
        </div>
      </div>
    </div>
  );
}

export default AmbulanceMap;
