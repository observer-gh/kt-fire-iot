import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import streamlit as st

from ..fire_detection_consumer import get_recent_fire_events, start_fire_detection_consumer
from ..models import FireDetectionNotifiedEvent

logger = logging.getLogger(__name__)


class FireAlertManager:
    """Manages fire detection alerts for video display"""

    def __init__(self):
        self._initialize_session_state()
        self._consumer_started = False

    def _initialize_session_state(self):
        """Initialize Streamlit session state for fire alerts"""
        if 'current_alert_severity' not in st.session_state:
            st.session_state.current_alert_severity = "normal"

        if 'active_fire_alerts' not in st.session_state:
            st.session_state.active_fire_alerts = []

        if 'last_fire_alert_check' not in st.session_state:
            st.session_state.last_fire_alert_check = datetime.utcnow()

        if 'fire_consumer_error' not in st.session_state:
            st.session_state.fire_consumer_error = None

    async def ensure_consumer_started(self) -> bool:
        """Ensure fire detection consumer is running"""
        if not self._consumer_started:
            try:
                await start_fire_detection_consumer()
                self._consumer_started = True
                st.session_state.fire_consumer_error = None
                logger.info("Fire detection consumer started")
                return True
            except Exception as e:
                error_msg = f"Failed to start fire detection consumer: {e}"
                st.session_state.fire_consumer_error = error_msg
                logger.error(error_msg)
                return False
        return True

    async def check_fire_alerts(self) -> str:
        """Check for recent fire detection alerts and return current severity"""
        try:
            # Ensure consumer is running
            if not await self.ensure_consumer_started():
                return "normal"

            # Get recent fire events (last 5 minutes)
            recent_events = await get_recent_fire_events(limit=50)

            if not recent_events:
                st.session_state.current_alert_severity = "normal"
                st.session_state.active_fire_alerts = []
                return "normal"

            # Filter events from last 5 minutes
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            active_alerts = []

            for event in recent_events:
                # Parse created_at timestamp
                try:
                    if event.created_at.endswith('Z'):
                        event_time = datetime.fromisoformat(
                            event.created_at[:-1])
                    else:
                        event_time = datetime.fromisoformat(event.created_at)

                    if event_time > cutoff_time:
                        active_alerts.append(event)
                except Exception as e:
                    logger.warning(f"Failed to parse event timestamp: {e}")
                    continue

            # Determine highest severity from active alerts
            severity = self._determine_highest_severity(active_alerts)

            # Update session state
            st.session_state.current_alert_severity = severity
            st.session_state.active_fire_alerts = active_alerts
            st.session_state.last_fire_alert_check = datetime.utcnow()

            return severity

        except Exception as e:
            error_msg = f"Error checking fire alerts: {e}"
            logger.error(error_msg)
            st.session_state.fire_consumer_error = error_msg
            return "normal"

    def _determine_highest_severity(self, alerts: List[FireDetectionNotifiedEvent]) -> str:
        """Determine the highest severity from a list of alerts"""
        if not alerts:
            return "normal"

        # Priority: EMERGENCY > WARN > INFO
        severity_priority = {
            "EMERGENCY": 3,
            "WARN": 2,
            "INFO": 1
        }

        highest_priority = 0
        highest_severity = "normal"

        for alert in alerts:
            priority = severity_priority.get(alert.severity, 0)
            if priority > highest_priority:
                highest_priority = priority
                highest_severity = alert.severity

        return highest_severity if highest_severity != "normal" else "normal"

    def get_current_severity(self) -> str:
        """Get the current alert severity"""
        self._initialize_session_state()
        return st.session_state.current_alert_severity

    def get_active_alerts(self) -> List[FireDetectionNotifiedEvent]:
        """Get currently active fire alerts"""
        self._initialize_session_state()
        return st.session_state.active_fire_alerts

    def get_alert_summary(self) -> dict:
        """Get summary of current alert status"""
        # Ensure session state is initialized
        self._initialize_session_state()

        active_alerts = self.get_active_alerts()
        severity = self.get_current_severity()

        summary = {
            "total_alerts": len(active_alerts),
            "current_severity": severity,
            "emergency_count": len([a for a in active_alerts if a.severity == "EMERGENCY"]),
            "warning_count": len([a for a in active_alerts if a.severity == "WARN"]),
            "info_count": len([a for a in active_alerts if a.severity == "INFO"]),
            "last_check": st.session_state.last_fire_alert_check,
            "consumer_error": st.session_state.fire_consumer_error
        }

        return summary

    def format_alert_message(self, alert: FireDetectionNotifiedEvent) -> str:
        """Format alert for display"""
        severity_icons = {
            "EMERGENCY": "🚨",
            "WARN": "⚠️",
            "INFO": "ℹ️"
        }

        icon = severity_icons.get(alert.severity, "🔥")

        message = f"{icon} **{alert.severity}** Fire Alert"
        message += f"\n- **Alert ID**: {alert.alert_id}"
        message += f"\n- **Facility**: {alert.facility_id or 'Unknown'}"
        message += f"\n- **Location**: {alert.equipment_location or 'Unknown'}"
        message += f"\n- **Type**: {alert.alert_type}"
        message += f"\n- **Description**: {alert.description}"

        if alert.detection_confidence:
            message += f"\n- **Confidence**: {alert.detection_confidence}%"

        if alert.cctv_id:
            message += f"\n- **CCTV**: {alert.cctv_id}"

        return message


def create_fire_alert_display(fire_alert_manager: FireAlertManager):
    """Create fire alert status display"""
    alert_summary = fire_alert_manager.get_alert_summary()

    st.subheader("🔥 Fire Detection Alerts")

    # Show consumer error if any
    if alert_summary["consumer_error"]:
        st.error(
            f"❌ Fire Detection Consumer Error: {alert_summary['consumer_error']}")
        return

    # Alert summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_alerts = alert_summary["total_alerts"]
        st.metric("🚨 Active Alerts", total_alerts)

    with col2:
        emergency_count = alert_summary["emergency_count"]
        st.metric("🚨 Emergency", emergency_count,
                  delta=None if emergency_count == 0 else "🚨")

    with col3:
        warning_count = alert_summary["warning_count"]
        st.metric("⚠️ Warnings", warning_count,
                  delta=None if warning_count == 0 else "⚠️")

    with col4:
        info_count = alert_summary["info_count"]
        st.metric("ℹ️ Info", info_count)

    # Current severity status
    current_severity = alert_summary["current_severity"]

    if current_severity == "EMERGENCY":
        st.error("🚨 **EMERGENCY FIRE ALERT ACTIVE** 🚨")
    elif current_severity == "WARN":
        st.warning("⚠️ **Fire Warning Active** ⚠️")
    elif current_severity == "INFO":
        st.info("ℹ️ Fire Detection Information")
    else:
        st.success("✅ No Active Fire Alerts")

    # Display individual alerts
    active_alerts = fire_alert_manager.get_active_alerts()

    if active_alerts:
        st.subheader("📋 Active Fire Alerts Details")

        # Show up to 5 most recent
        for i, alert in enumerate(active_alerts[:5]):
            with st.expander(f"Alert {i+1}: {alert.severity} - {alert.alert_type}", expanded=(i == 0)):
                alert_message = fire_alert_manager.format_alert_message(alert)
                st.markdown(alert_message)

                # Show timestamp
                st.caption(f"Created: {alert.created_at}")

    # Last check info
    last_check = alert_summary["last_check"]
    if last_check:
        time_since_check = datetime.utcnow() - last_check
        st.caption(
            f"Last checked: {int(time_since_check.total_seconds())} seconds ago")


# Global instance - lazy initialization to avoid import issues
_fire_alert_manager = None


def get_fire_alert_manager() -> FireAlertManager:
    """Get the global fire alert manager"""
    global _fire_alert_manager
    if _fire_alert_manager is None:
        _fire_alert_manager = FireAlertManager()
    return _fire_alert_manager


async def get_current_alert_severity() -> str:
    """Get current fire alert severity (async helper for dashboard)"""
    manager = get_fire_alert_manager()
    return await manager.check_fire_alerts()
