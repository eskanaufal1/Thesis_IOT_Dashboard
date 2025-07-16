"""
Dependency injection for global services.
"""

from app.services.enhanced_mqtt_service import enhanced_mqtt_service
from typing import Optional


def get_enhanced_mqtt_service():
    """
    Get the enhanced MQTT service instance.
    
    Returns:
        EnhancedMQTTService: Enhanced MQTT service instance
    """
    return enhanced_mqtt_service
