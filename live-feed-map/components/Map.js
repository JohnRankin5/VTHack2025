// components/Map.js
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const Map = () => {
  return (
    <div style={{ height: '500px' }}>
      <MapContainer center={[51.505, -0.09]} zoom={13} style={{ height: '100%', width: '100%' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {/* Example Marker */}
        <Marker position={[51.505, -0.09]}>
          <Popup>A marker!</Popup>
        </Marker>
      </MapContainer>
    </div>
  );
};

export default Map;
