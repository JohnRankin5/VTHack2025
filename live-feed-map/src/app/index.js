// pages/index.js
import Map from '../components/Map';
import LiveFeed from '../components/LiveFeed';
import Status from '../components/Status';

export default function Home() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Firefighter Helmet HUD</h1>
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {/* Live Feed Section */}
        <LiveFeed />
        
        {/* Map Section */}
        <Map />

        {/* Status Section */}
        <Status />
      </div>
    </div>
  );
}
