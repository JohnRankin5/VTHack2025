#!/usr/bin/env python3
"""
Radar Data Simulator
Simulates radar distance measurements for testing the HUD system
"""

import asyncio
import websockets
import json
import time
import math
import random

async def simulate_radar_data():
    """Simulate realistic radar distance measurements"""
    
    # Try to connect to the WebSocket data bridge
    uri = "ws://localhost:65431"  # Local testing
    
    try:
        async with websockets.connect(uri) as websocket:
            print("🔗 Connected to radar data receiver")
            print("📡 Starting radar simulation...")
            
            base_distance = 3.0  # Base distance in meters
            time_start = time.time()
            
            while True:
                # Simulate realistic distance changes
                elapsed = time.time() - time_start
                
                # Create a scenario where distance varies
                distance_variation = math.sin(elapsed * 0.1) * 2.0  # Slow oscillation
                noise = random.uniform(-0.1, 0.1)  # Small random noise
                
                simulated_distance = base_distance + distance_variation + noise
                simulated_distance = max(0.1, simulated_distance)  # Minimum 0.1m
                
                # Create radar data packet
                radar_packet = {
                    "type": "radar_distance",
                    "distance_m": round(simulated_distance, 3),
                    "t_sec": time.time()
                }
                
                # Send the data
                await websocket.send(json.dumps(radar_packet))
                print(f"📡 Sent: Distance = {simulated_distance:.2f}m")
                
                # Wait before next reading (simulate ~10Hz radar)
                await asyncio.sleep(0.1)
                
    except ConnectionRefusedError:
        print("❌ Could not connect to radar receiver")
        print("💡 Make sure the WebSocket data bridge is running first")
    except Exception as e:
        print(f"❌ Simulator error: {e}")

async def simulate_scenarios():
    """Simulate different distance scenarios for testing"""
    scenarios = [
        {"name": "Safe Distance", "distance": 5.0, "duration": 5},
        {"name": "Warning Zone", "distance": 1.5, "duration": 3},
        {"name": "Critical Zone", "distance": 0.8, "duration": 2},
        {"name": "Emergency!", "distance": 0.3, "duration": 2},
        {"name": "Backing Away", "distance": 2.5, "duration": 3}
    ]
    
    uri = "ws://localhost:65431"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("🎭 Running radar scenarios simulation...")
            
            for scenario in scenarios:
                print(f"\n🎬 Scenario: {scenario['name']} - {scenario['distance']}m")
                
                for i in range(scenario['duration'] * 10):  # 10Hz for duration seconds
                    # Add small random variations
                    distance = scenario['distance'] + random.uniform(-0.05, 0.05)
                    
                    radar_packet = {
                        "type": "radar_distance", 
                        "distance_m": round(distance, 3),
                        "t_sec": time.time()
                    }
                    
                    await websocket.send(json.dumps(radar_packet))
                    await asyncio.sleep(0.1)
                
            print("\n✅ All scenarios completed!")
            
    except ConnectionRefusedError:
        print("❌ Could not connect to radar receiver")
        print("💡 Make sure the WebSocket data bridge is running first")

def main():
    """Main function"""
    print("=" * 50)
    print("📡 RADAR DATA SIMULATOR")
    print("=" * 50)
    print("Choose simulation mode:")
    print("1. Continuous simulation (realistic distance changes)")
    print("2. Scenario testing (predefined test cases)")
    print("3. Manual distance input")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🔄 Starting continuous radar simulation...")
        print("📊 Distance will vary between 1-5 meters")
        print("⚠️  Press Ctrl+C to stop")
        asyncio.run(simulate_radar_data())
    elif choice == "2":
        print("\n🎭 Starting scenario testing...")
        asyncio.run(simulate_scenarios())
    elif choice == "3":
        asyncio.run(manual_input_mode())
    else:
        print("❌ Invalid choice")

async def manual_input_mode():
    """Allow manual distance input for testing"""
    uri = "ws://localhost:65431"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("🎮 Manual radar input mode")
            print("💡 Enter distances in meters (or 'quit' to exit)")
            
            while True:
                distance_input = input("\nEnter distance (m): ").strip()
                
                if distance_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                try:
                    distance = float(distance_input)
                    if distance < 0:
                        print("❌ Distance must be positive")
                        continue
                    
                    radar_packet = {
                        "type": "radar_distance",
                        "distance_m": distance,
                        "t_sec": time.time()
                    }
                    
                    await websocket.send(json.dumps(radar_packet))
                    print(f"📡 Sent: {distance}m")
                    
                except ValueError:
                    print("❌ Invalid number format")
                    
    except ConnectionRefusedError:
        print("❌ Could not connect to radar receiver")

if __name__ == "__main__":
    main()
