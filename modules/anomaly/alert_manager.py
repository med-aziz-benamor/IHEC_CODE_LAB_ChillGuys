"""
Alert Manager
=============
Tracks anomaly alerts and user actions with JSON persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path


@dataclass
class AlertAction:
    action_type: str
    timestamp: str
    user_notes: str = ""


class AlertManager:
    """
    Manages anomaly alerts and user actions.

    Attributes:
        alerts: List of alert dicts
        actions: Dict mapping alert_id -> action details
    """

    def __init__(self):
        self.alerts: List[Dict] = []
        self.actions: Dict[str, Dict] = {}
        self.autosave_path: Optional[str] = None

    def register_alert(self, alert: Dict) -> None:
        """Register a new alert if not already present."""
        alert_id = alert.get('alert_id')
        if not alert_id:
            return
        if any(a.get('alert_id') == alert_id for a in self.alerts):
            return
        self.alerts.append(alert)

    def record_action(self, alert_id: str, action_type: str, user_notes: str = "") -> None:
        """
        Record a user action for a specific alert.

        Args:
            alert_id: Unique alert identifier
            action_type: 'ignored' | 'investigated' | 'traded' | 'reported'
            user_notes: Optional notes
        """
        action = AlertAction(
            action_type=action_type,
            timestamp=datetime.now().isoformat(),
            user_notes=user_notes or "",
        )
        self.actions[alert_id] = {
            'action_type': action.action_type,
            'timestamp': action.timestamp,
            'user_notes': action.user_notes,
        }
        if self.autosave_path:
            self.save_to_file(self.autosave_path)

    def get_alert_history(self, lookback_days: int = 7) -> List[Dict]:
        """
        Return alerts with associated actions within a lookback window.
        """
        cutoff = datetime.now() - timedelta(days=lookback_days)
        history = []

        for alert in self.alerts:
            alert_ts = self._parse_alert_timestamp(alert)
            if alert_ts and alert_ts < cutoff:
                continue
            entry = dict(alert)
            action = self.actions.get(alert.get('alert_id'))
            if action:
                entry['action'] = action
            history.append(entry)

        return history

    def get_unactioned_alerts(self) -> List[Dict]:
        """Return alerts that have no recorded action."""
        unactioned = []
        for alert in self.alerts:
            alert_id = alert.get('alert_id')
            if alert_id and alert_id not in self.actions:
                unactioned.append(alert)
        return unactioned

    def save_to_file(self, filepath: str) -> None:
        """Persist alerts/actions to JSON."""
        path = Path(filepath)
        data = {
            'alerts': self.alerts,
            'actions': self.actions,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath: str) -> None:
        """Load alerts/actions from JSON if the file exists."""
        path = Path(filepath)
        if not path.exists():
            return
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        self.alerts = data.get('alerts', [])
        self.actions = data.get('actions', {})

    @staticmethod
    def _parse_alert_timestamp(alert: Dict) -> Optional[datetime]:
        ts = alert.get('timestamp') or alert.get('date')
        if not ts:
            return None
        try:
            return datetime.fromisoformat(ts)
        except Exception:
            return None


_DEFAULT_MANAGER: Optional[AlertManager] = None


def get_default_alert_manager() -> AlertManager:
    """Return a module-level singleton AlertManager."""
    global _DEFAULT_MANAGER
    if _DEFAULT_MANAGER is None:
        _DEFAULT_MANAGER = AlertManager()
    return _DEFAULT_MANAGER
