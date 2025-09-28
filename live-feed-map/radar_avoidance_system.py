#!/usr/bin/env python3
"""
Radar-based Object Avoidance System
Integrates radar distance measurements with video feed for collision avoidance
"""

import asyncio
import json
import time
import numpy as np
from datetime import datetime
from collections import deque
import statistics
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RadarAvoidanceSystem:
    def __init__(self, min_safe_distance=1.0, warning_distance=2.0, critical_distance=0.5):
        """
        Initialize radar-based object avoidance system
        
        Args:
            min_safe_distance (float): Minimum safe distance in meters
            warning_distance (float): Distance at which to show warnings in meters
            critical_distance (float): Distance at which to trigger emergency alerts in meters
        """
        self.min_safe_distance = min_safe_distance
        self.warning_distance = warning_distance
        self.critical_distance = critical_distance
        
        # Data storage
        self.distance_history = deque(maxlen=30)  # Keep last 30 readings (~1 second at 30Hz)
        self.current_distance = None
        self.filtered_distance = None
        
        # Avoidance state
        self.avoidance_status = "SAFE"  # SAFE, WARNING, CRITICAL, EMERGENCY
        self.last_update_time = None
        
        # Movement recommendations
        self.movement_recommendation = None
        self.obstacle_direction = None
        
        # Alert system
        self.alert_history = deque(maxlen=100)
        self.consecutive_alerts = 0
        
        logger.info(f"🔧 Radar Avoidance System initialized:")
        logger.info(f"   Safe distance: {min_safe_distance}m")
        logger.info(f"   Warning distance: {warning_distance}m") 
        logger.info(f"   Critical distance: {critical_distance}m")

    def process_radar_data(self, radar_data):
        """
        Process incoming radar data and update avoidance system
        
        Args:
            radar_data (dict): Radar data with distance_m and t_sec
        """
        try:
            distance_m = radar_data.get('distance_m', None)
            timestamp = radar_data.get('t_sec', time.time())
            
            if distance_m is None:
                logger.warning("⚠️ Received radar data without distance measurement")
                return
            
            # Store raw distance
            self.current_distance = distance_m
            self.last_update_time = timestamp
            
            # Add to history for filtering
            self.distance_history.append({
                'distance': distance_m,
                'timestamp': timestamp
            })
            
            # Apply filtering to reduce noise
            self.filtered_distance = self._apply_distance_filter()
            
            # Update avoidance status
            self._update_avoidance_status()
            
            # Generate movement recommendations
            self._generate_movement_recommendations()
            
            # Log critical situations
            if self.avoidance_status in ["CRITICAL", "EMERGENCY"]:
                logger.warning(f"🚨 {self.avoidance_status}: Distance {self.filtered_distance:.2f}m")
            
        except Exception as e:
            logger.error(f"❌ Error processing radar data: {e}")

    def _apply_distance_filter(self):
        """Apply filtering to reduce noise in distance measurements"""
        if len(self.distance_history) < 3:
            return self.current_distance
        
        # Get recent distances
        recent_distances = [entry['distance'] for entry in list(self.distance_history)[-10:]]
        
        # Apply median filter to reduce noise
        filtered = statistics.median(recent_distances)
        
        # Apply additional smoothing for very recent readings
        if len(recent_distances) >= 5:
            # Weighted average of median and recent readings
            recent_avg = statistics.mean(recent_distances[-3:])
            filtered = 0.7 * filtered + 0.3 * recent_avg
        
        return filtered

    def _update_avoidance_status(self):
        """Update the current avoidance status based on filtered distance"""
        if self.filtered_distance is None:
            self.avoidance_status = "NO_DATA"
            return
        
        previous_status = self.avoidance_status
        
        if self.filtered_distance <= self.critical_distance:
            self.avoidance_status = "EMERGENCY"
            self.consecutive_alerts += 1
        elif self.filtered_distance <= self.min_safe_distance:
            self.avoidance_status = "CRITICAL" 
            self.consecutive_alerts += 1
        elif self.filtered_distance <= self.warning_distance:
            self.avoidance_status = "WARNING"
            if previous_status in ["CRITICAL", "EMERGENCY"]:
                self.consecutive_alerts = max(0, self.consecutive_alerts - 1)
        else:
            self.avoidance_status = "SAFE"
            self.consecutive_alerts = 0
        
        # Log status changes
        if previous_status != self.avoidance_status:
            logger.info(f"🔄 Status changed: {previous_status} → {self.avoidance_status}")
            
            # Add to alert history
            self.alert_history.append({
                'timestamp': time.time(),
                'status': self.avoidance_status,
                'distance': self.filtered_distance,
                'previous_status': previous_status
            })

    def _generate_movement_recommendations(self):
        """Generate movement recommendations based on current situation"""
        if self.filtered_distance is None:
            self.movement_recommendation = "NO_DATA"
            return
        
        if self.avoidance_status == "EMERGENCY":
            self.movement_recommendation = "STOP_IMMEDIATELY"
        elif self.avoidance_status == "CRITICAL":
            self.movement_recommendation = "REVERSE_SLOWLY"
        elif self.avoidance_status == "WARNING":
            self.movement_recommendation = "SLOW_DOWN"
        else:
            self.movement_recommendation = "PROCEED_NORMAL"
        
        # Determine obstacle direction (simplified - assumes front-facing radar)
        self.obstacle_direction = "FRONT"

    def get_hud_data(self):
        """Get data for HUD display"""
        return {
            'distance_m': self.filtered_distance,
            'raw_distance_m': self.current_distance,
            'status': self.avoidance_status,
            'movement_recommendation': self.movement_recommendation,
            'obstacle_direction': self.obstacle_direction,
            'last_update': self.last_update_time,
            'consecutive_alerts': self.consecutive_alerts,
            'distance_trend': self._get_distance_trend(),
            'safety_zones': {
                'safe': self.warning_distance,
                'warning': self.min_safe_distance,
                'critical': self.critical_distance
            }
        }

    def _get_distance_trend(self):
        """Analyze if distance is increasing or decreasing"""
        if len(self.distance_history) < 5:
            return "STABLE"
        
        recent_distances = [entry['distance'] for entry in list(self.distance_history)[-5:]]
        
        # Simple trend analysis
        if recent_distances[-1] > recent_distances[0] + 0.1:
            return "INCREASING"
        elif recent_distances[-1] < recent_distances[0] - 0.1:
            return "DECREASING" 
        else:
            return "STABLE"

    def get_collision_warning(self):
        """Get collision warning information"""
        if self.avoidance_status == "EMERGENCY":
            return {
                'level': 'EMERGENCY',
                'message': f'COLLISION IMMINENT! Distance: {self.filtered_distance:.1f}m',
                'color': '#FF0000',
                'action': 'STOP IMMEDIATELY',
                'sound_alert': True
            }
        elif self.avoidance_status == "CRITICAL":
            return {
                'level': 'CRITICAL',
                'message': f'DANGER: Object too close! Distance: {self.filtered_distance:.1f}m', 
                'color': '#FF6600',
                'action': 'REVERSE SLOWLY',
                'sound_alert': True
            }
        elif self.avoidance_status == "WARNING":
            return {
                'level': 'WARNING',
                'message': f'Caution: Object ahead. Distance: {self.filtered_distance:.1f}m',
                'color': '#FFAA00', 
                'action': 'SLOW DOWN',
                'sound_alert': False
            }
        else:
            return None

    def get_distance_visualization(self):
        """Get data for distance visualization (like a radar display)"""
        if self.filtered_distance is None:
            return None
        
        # Create a simple radar-like visualization data
        max_range = max(self.warning_distance * 2, 5.0)  # At least 5m range
        
        return {
            'current_distance': self.filtered_distance,
            'max_range': max_range,
            'normalized_distance': min(self.filtered_distance / max_range, 1.0),
            'zones': [
                {'name': 'CRITICAL', 'range': self.critical_distance, 'color': '#FF0000'},
                {'name': 'DANGER', 'range': self.min_safe_distance, 'color': '#FF6600'},
                {'name': 'WARNING', 'range': self.warning_distance, 'color': '#FFAA00'},
                {'name': 'SAFE', 'range': max_range, 'color': '#00FF00'}
            ]
        }

    def reset_system(self):
        """Reset the avoidance system"""
        self.distance_history.clear()
        self.current_distance = None
        self.filtered_distance = None
        self.avoidance_status = "SAFE"
        self.consecutive_alerts = 0
        logger.info("🔄 Radar avoidance system reset")

    def get_system_stats(self):
        """Get system statistics"""
        return {
            'total_readings': len(self.distance_history),
            'current_status': self.avoidance_status,
            'total_alerts': len(self.alert_history),
            'consecutive_alerts': self.consecutive_alerts,
            'average_distance': statistics.mean([e['distance'] for e in self.distance_history]) if self.distance_history else None,
            'last_update': self.last_update_time,
            'system_health': 'HEALTHY' if self.last_update_time and (time.time() - self.last_update_time) < 2.0 else 'STALE_DATA'
        }


class RadarDataManager:
    """Manages radar data integration with existing websocket system"""
    
    def __init__(self, websocket_data_store):
        self.data_store = websocket_data_store
        self.avoidance_system = RadarAvoidanceSystem()
        self.last_processed_id = 0
        
    def process_new_radar_data(self):
        """Process new radar data from the websocket data store"""
        try:
            # Get latest laptop data (radar data)
            latest_data = self.data_store.get_latest(50)  # Get more data to ensure we don't miss any
            
            # Filter for radar data from laptop
            radar_entries = [
                entry for entry in latest_data 
                if entry.get('device_type') == 'laptop' and 
                entry.get('processed_data', {}).get('type') == 'radar_distance'
                and entry.get('id', 0) > self.last_processed_id
            ]
            
            # Process new radar entries
            for entry in radar_entries:
                processed_data = entry.get('processed_data', {})
                if 'distance_m' in processed_data:
                    self.avoidance_system.process_radar_data(processed_data)
                    self.last_processed_id = entry.get('id', 0)
                    
            return len(radar_entries)
            
        except Exception as e:
            logger.error(f"❌ Error processing radar data: {e}")
            return 0
    
    def get_avoidance_data(self):
        """Get current avoidance system data"""
        return {
            'hud_data': self.avoidance_system.get_hud_data(),
            'collision_warning': self.avoidance_system.get_collision_warning(),
            'distance_visualization': self.avoidance_system.get_distance_visualization(),
            'system_stats': self.avoidance_system.get_system_stats()
        }
