"""
n8n Webhook Integration for NextFlow.

This module handles sending events to n8n workflows via webhooks.
"""
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

from src.config.settings import n8n_settings


class N8NWebhook:
    """Handle webhook communications with n8n."""

    def __init__(self):
        self.webhook_url = n8n_settings.webhook_url
        self.enabled = n8n_settings.enabled
        self.secret = n8n_settings.secret

    def send_event(self, event_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send an event to n8n webhook.

        Args:
            event_type: Type of event (order_created, order_updated, order_deleted, etc.)
            data: Event data to send

        Returns:
            Dict: Response data from n8n if successful, None otherwise
        """
        if not self.enabled:
            logger.debug("n8n webhooks are disabled")
            return None

        try:
            payload = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "source": "NextFlow",
                "data": data
            }

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "NextFlow/1.0"
            }

            # Add secret header if configured
            if self.secret:
                headers["X-N8N-Secret"] = self.secret

            logger.info(f"Sending {event_type} event to n8n: {self.webhook_url}")

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Event {event_type} sent successfully to n8n")
                try:
                    return response.json()
                except:
                    return {"status": "success", "message": "Event received"}
            else:
                logger.warning(f"⚠️ n8n webhook returned status {response.status_code}: {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout sending event to n8n: {event_type}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Connection error sending event to n8n: {event_type}")
            return None
        except Exception as e:
            logger.error(f"❌ Error sending event to n8n: {e}")
            return None

    def send_order_created(self, order_data: Dict[str, Any]) -> bool:
        """Send order created event to n8n."""
        return self.send_event("order.created", order_data)

    def send_order_updated(self, order_id: int, order_data: Dict[str, Any]) -> bool:
        """Send order updated event to n8n."""
        return self.send_event("order.updated", {
            "order_id": order_id,
            **order_data
        })

    def send_order_deleted(self, order_id: int) -> bool:
        """Send order deleted event to n8n."""
        return self.send_event("order.deleted", {"order_id": order_id})

    def send_order_status_changed(self, order_id: int, old_status: str, new_status: str) -> bool:
        """Send order status changed event to n8n."""
        return self.send_event("order.status_changed", {
            "order_id": order_id,
            "old_status": old_status,
            "new_status": new_status
        })

    def send_bulk_status_update(self, order_ids: list, new_status: str, updated_count: int) -> bool:
        """Send bulk status update event to n8n."""
        return self.send_event("order.bulk_status_update", {
            "order_ids": order_ids,
            "new_status": new_status,
            "updated_count": updated_count
        })

    def send_low_stock_alert(self, product: str, current_stock: int, threshold: int) -> bool:
        """Send low stock alert to n8n."""
        return self.send_event("inventory.low_stock", {
            "product": product,
            "current_stock": current_stock,
            "threshold": threshold
        })

    def send_high_value_order(self, order_id: int, amount: float, customer: str) -> bool:
        """Send high value order alert to n8n."""
        return self.send_event("order.high_value", {
            "order_id": order_id,
            "amount": amount,
            "customer": customer
        })

    def send_daily_summary(self, summary_data: Dict[str, Any]) -> bool:
        """Send daily summary to n8n."""
        return self.send_event("report.daily_summary", summary_data)

    def test_connection(self) -> bool:
        """Test the n8n webhook connection."""
        return self.send_event("test.connection", {
            "message": "Testing n8n webhook connection from NextFlow"
        })


# Global instance
n8n_webhook = N8NWebhook()
