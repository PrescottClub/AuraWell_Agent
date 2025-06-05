"""
Notification Service for AuraWell

Handles user notifications, alerts, and communication.
Supports multiple notification channels and delivery methods.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass

from .base_service import BaseService, ServiceResult, ServiceStatus
from ..models.enums import NotificationType, NotificationChannel, NotificationPriority

logger = logging.getLogger(__name__)


@dataclass
class Notification:
    """Notification data structure"""
    notification_id: str
    user_id: str
    notification_type: NotificationType
    channel: NotificationChannel
    priority: NotificationPriority
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class NotificationService(BaseService):
    """
    Service for managing user notifications
    
    Provides async methods for:
    - Sending notifications across multiple channels
    - Scheduling notifications
    - Managing notification preferences
    - Tracking delivery and read status
    """
    
    def __init__(self, database_manager=None):
        """
        Initialize notification service
        
        Args:
            database_manager: Database manager instance
        """
        super().__init__("NotificationService")
        self.database_manager = database_manager
        self._notification_queue: List[Notification] = []
        self._delivery_stats = {
            "sent": 0,
            "failed": 0,
            "pending": 0
        }
        self._channel_handlers = {}
        self._user_preferences = {}  # Cache for user notification preferences
    
    async def _initialize_service(self) -> None:
        """Initialize notification service"""
        # Initialize default channel handlers
        self._channel_handlers = {
            NotificationChannel.IN_APP: self._handle_in_app_notification,
            NotificationChannel.EMAIL: self._handle_email_notification,
            NotificationChannel.SMS: self._handle_sms_notification,
            NotificationChannel.PUSH: self._handle_push_notification,
            NotificationChannel.WEBHOOK: self._handle_webhook_notification
        }
        
        # Start background task for processing notifications
        asyncio.create_task(self._process_notification_queue())
        
        self.logger.info("Notification service initialized")
    
    async def _shutdown_service(self) -> None:
        """Shutdown notification service"""
        # Process remaining notifications
        await self._flush_notification_queue()
        self._notification_queue.clear()
        self._user_preferences.clear()
        self.logger.info("Notification service shutdown")
    
    async def _perform_health_check(self) -> Optional[Dict[str, Any]]:
        """Perform notification service health check"""
        health_details = {
            "queue_size": len(self._notification_queue),
            "delivery_stats": self._delivery_stats.copy(),
            "channel_handlers": list(self._channel_handlers.keys()),
            "cached_preferences": len(self._user_preferences)
        }
        
        # Check if queue is getting too large
        if len(self._notification_queue) > 1000:
            self._health_status = ServiceStatus.DEGRADED
            health_details["warning"] = "Notification queue is large"
        
        return health_details
    
    async def send_notification(self, user_id: str, notification_type: NotificationType,
                               title: str, message: str, 
                               channel: Optional[NotificationChannel] = None,
                               priority: NotificationPriority = NotificationPriority.MEDIUM,
                               data: Optional[Dict[str, Any]] = None,
                               scheduled_at: Optional[datetime] = None) -> ServiceResult[str]:
        """
        Send notification to user
        
        Args:
            user_id: User identifier
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            channel: Preferred delivery channel (auto-select if None)
            priority: Notification priority
            data: Additional notification data
            scheduled_at: Schedule notification for later (None for immediate)
            
        Returns:
            ServiceResult with notification ID
        """
        try:
            # Generate notification ID
            notification_id = f"notif_{user_id}_{int(datetime.now().timestamp())}"
            
            # Auto-select channel if not specified
            if channel is None:
                channel = await self._select_best_channel(user_id, notification_type, priority)
            
            # Create notification
            notification = Notification(
                notification_id=notification_id,
                user_id=user_id,
                notification_type=notification_type,
                channel=channel,
                priority=priority,
                title=title,
                message=message,
                data=data,
                scheduled_at=scheduled_at,
                created_at=datetime.now(timezone.utc)
            )
            
            # Add to queue
            self._notification_queue.append(notification)
            self._delivery_stats["pending"] += 1
            
            self.logger.info(f"Notification {notification_id} queued for user {user_id}")
            return ServiceResult.success_result(notification_id)
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="NOTIFICATION_ERROR"
            )
    
    async def send_health_insight_notification(self, user_id: str, insight: Dict[str, Any]) -> ServiceResult[str]:
        """
        Send health insight notification
        
        Args:
            user_id: User identifier
            insight: Health insight data
            
        Returns:
            ServiceResult with notification ID
        """
        try:
            title = f"新的健康洞察: {insight.get('title', '健康分析')}"
            message = insight.get('description', '我们为您生成了新的健康洞察')
            
            # Determine priority based on insight priority
            insight_priority = insight.get('priority', 'medium')
            if insight_priority == 'critical':
                priority = NotificationPriority.URGENT
            elif insight_priority == 'high':
                priority = NotificationPriority.HIGH
            else:
                priority = NotificationPriority.MEDIUM
            
            return await self.send_notification(
                user_id=user_id,
                notification_type=NotificationType.HEALTH_INSIGHT,
                title=title,
                message=message,
                priority=priority,
                data={"insight_id": insight.get('insight_id')}
            )
            
        except Exception as e:
            self.logger.error(f"Error sending health insight notification: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="INSIGHT_NOTIFICATION_ERROR"
            )
    
    async def send_goal_reminder(self, user_id: str, goal_type: str, 
                                current_progress: float, target: float) -> ServiceResult[str]:
        """
        Send goal reminder notification
        
        Args:
            user_id: User identifier
            goal_type: Type of goal (steps, sleep, etc.)
            current_progress: Current progress value
            target: Target value
            
        Returns:
            ServiceResult with notification ID
        """
        try:
            progress_percentage = (current_progress / target) * 100 if target > 0 else 0
            
            if progress_percentage < 50:
                title = f"目标提醒: {goal_type}"
                message = f"您今天的{goal_type}进度为{progress_percentage:.1f}%，加油完成目标！"
                priority = NotificationPriority.MEDIUM
            elif progress_percentage >= 100:
                title = f"目标达成: {goal_type}"
                message = f"恭喜！您已完成今天的{goal_type}目标！"
                priority = NotificationPriority.LOW
            else:
                title = f"目标进展: {goal_type}"
                message = f"您的{goal_type}进度为{progress_percentage:.1f}%，继续保持！"
                priority = NotificationPriority.LOW
            
            return await self.send_notification(
                user_id=user_id,
                notification_type=NotificationType.GOAL_REMINDER,
                title=title,
                message=message,
                priority=priority,
                data={
                    "goal_type": goal_type,
                    "current_progress": current_progress,
                    "target": target,
                    "progress_percentage": progress_percentage
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error sending goal reminder: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="GOAL_REMINDER_ERROR"
            )
    
    async def get_user_notifications(self, user_id: str, limit: int = 50, 
                                   unread_only: bool = False) -> ServiceResult[List[Dict[str, Any]]]:
        """
        Get notifications for user
        
        Args:
            user_id: User identifier
            limit: Maximum number of notifications
            unread_only: Only return unread notifications
            
        Returns:
            ServiceResult with list of notifications
        """
        try:
            # In a real implementation, this would query the database
            # For now, return notifications from queue and recent history
            user_notifications = []
            
            for notification in self._notification_queue:
                if notification.user_id == user_id:
                    if unread_only and notification.read_at is not None:
                        continue
                    
                    notification_dict = {
                        "notification_id": notification.notification_id,
                        "notification_type": notification.notification_type.value,
                        "channel": notification.channel.value,
                        "priority": notification.priority.value,
                        "title": notification.title,
                        "message": notification.message,
                        "data": notification.data,
                        "scheduled_at": notification.scheduled_at.isoformat() if notification.scheduled_at else None,
                        "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                        "read_at": notification.read_at.isoformat() if notification.read_at else None,
                        "created_at": notification.created_at.isoformat() if notification.created_at else None
                    }
                    user_notifications.append(notification_dict)
            
            # Sort by creation time (newest first)
            user_notifications.sort(key=lambda x: x["created_at"], reverse=True)
            
            return ServiceResult.success_result(user_notifications[:limit])
            
        except Exception as e:
            self.logger.error(f"Error getting notifications for user {user_id}: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="GET_NOTIFICATIONS_ERROR"
            )
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> ServiceResult[bool]:
        """
        Mark notification as read
        
        Args:
            notification_id: Notification identifier
            user_id: User identifier
            
        Returns:
            ServiceResult with success status
        """
        try:
            # Find notification in queue
            for notification in self._notification_queue:
                if (notification.notification_id == notification_id and 
                    notification.user_id == user_id):
                    notification.read_at = datetime.now(timezone.utc)
                    self.logger.info(f"Notification {notification_id} marked as read")
                    return ServiceResult.success_result(True)
            
            return ServiceResult.error_result(
                error="Notification not found",
                error_code="NOTIFICATION_NOT_FOUND"
            )
            
        except Exception as e:
            self.logger.error(f"Error marking notification as read: {e}")
            return ServiceResult.error_result(
                error=str(e),
                error_code="MARK_READ_ERROR"
            )
    
    async def _process_notification_queue(self) -> None:
        """Background task to process notification queue"""
        while True:
            try:
                await asyncio.sleep(5)  # Process every 5 seconds
                
                if not self._notification_queue:
                    continue
                
                # Process notifications that are ready to send
                notifications_to_send = []
                now = datetime.now(timezone.utc)
                
                for notification in self._notification_queue[:]:
                    if notification.sent_at is not None:
                        continue  # Already sent
                    
                    if (notification.scheduled_at is None or 
                        notification.scheduled_at <= now):
                        notifications_to_send.append(notification)
                
                # Send notifications
                for notification in notifications_to_send:
                    await self._deliver_notification(notification)
                
            except Exception as e:
                self.logger.error(f"Error in notification queue processing: {e}")
    
    async def _deliver_notification(self, notification: Notification) -> bool:
        """
        Deliver a single notification
        
        Args:
            notification: Notification to deliver
            
        Returns:
            True if delivery successful, False otherwise
        """
        try:
            handler = self._channel_handlers.get(notification.channel)
            if not handler:
                self.logger.error(f"No handler for channel {notification.channel}")
                return False
            
            # Call channel handler
            success = await handler(notification)
            
            if success:
                notification.sent_at = datetime.now(timezone.utc)
                self._delivery_stats["sent"] += 1
                self._delivery_stats["pending"] -= 1
                self.logger.info(f"Notification {notification.notification_id} delivered via {notification.channel}")
            else:
                self._delivery_stats["failed"] += 1
                self._delivery_stats["pending"] -= 1
                self.logger.error(f"Failed to deliver notification {notification.notification_id}")
            
            return success
            
        except Exception as e:
            self._delivery_stats["failed"] += 1
            self._delivery_stats["pending"] -= 1
            self.logger.error(f"Error delivering notification {notification.notification_id}: {e}")
            return False

    async def _select_best_channel(self, user_id: str, notification_type: NotificationType,
                                  priority: NotificationPriority) -> NotificationChannel:
        """
        Select best notification channel for user

        Args:
            user_id: User identifier
            notification_type: Type of notification
            priority: Notification priority

        Returns:
            Best notification channel
        """
        # Get user preferences (cached or from database)
        preferences = self._user_preferences.get(user_id, {})

        # Default channel selection logic
        if priority == NotificationPriority.URGENT:
            return preferences.get('urgent_channel', NotificationChannel.PUSH)
        elif notification_type == NotificationType.HEALTH_INSIGHT:
            return preferences.get('insight_channel', NotificationChannel.IN_APP)
        elif notification_type == NotificationType.GOAL_REMINDER:
            return preferences.get('reminder_channel', NotificationChannel.PUSH)
        else:
            return preferences.get('default_channel', NotificationChannel.IN_APP)

    async def _handle_in_app_notification(self, notification: Notification) -> bool:
        """Handle in-app notification delivery"""
        try:
            # In a real implementation, this would store the notification
            # in a database table for the app to retrieve
            self.logger.info(f"In-app notification sent: {notification.title}")
            return True
        except Exception as e:
            self.logger.error(f"In-app notification failed: {e}")
            return False

    async def _handle_email_notification(self, notification: Notification) -> bool:
        """Handle email notification delivery"""
        try:
            # In a real implementation, this would integrate with an email service
            # like SendGrid, AWS SES, or SMTP
            self.logger.info(f"Email notification sent: {notification.title}")
            return True
        except Exception as e:
            self.logger.error(f"Email notification failed: {e}")
            return False

    async def _handle_sms_notification(self, notification: Notification) -> bool:
        """Handle SMS notification delivery"""
        try:
            # In a real implementation, this would integrate with an SMS service
            # like Twilio, AWS SNS, or similar
            self.logger.info(f"SMS notification sent: {notification.title}")
            return True
        except Exception as e:
            self.logger.error(f"SMS notification failed: {e}")
            return False

    async def _handle_push_notification(self, notification: Notification) -> bool:
        """Handle push notification delivery"""
        try:
            # In a real implementation, this would integrate with push services
            # like Firebase Cloud Messaging, Apple Push Notification Service, etc.
            self.logger.info(f"Push notification sent: {notification.title}")
            return True
        except Exception as e:
            self.logger.error(f"Push notification failed: {e}")
            return False

    async def _handle_webhook_notification(self, notification: Notification) -> bool:
        """Handle webhook notification delivery"""
        try:
            # In a real implementation, this would make HTTP requests to user-defined webhooks
            self.logger.info(f"Webhook notification sent: {notification.title}")
            return True
        except Exception as e:
            self.logger.error(f"Webhook notification failed: {e}")
            return False

    async def _flush_notification_queue(self) -> None:
        """Process all remaining notifications in queue"""
        try:
            notifications_to_send = [n for n in self._notification_queue if n.sent_at is None]

            for notification in notifications_to_send:
                await self._deliver_notification(notification)

            self.logger.info(f"Flushed {len(notifications_to_send)} notifications")

        except Exception as e:
            self.logger.error(f"Error flushing notification queue: {e}")

    def set_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """
        Set notification preferences for user

        Args:
            user_id: User identifier
            preferences: Notification preferences
        """
        self._user_preferences[user_id] = preferences
        self.logger.info(f"Updated notification preferences for user {user_id}")

    def get_delivery_statistics(self) -> Dict[str, Any]:
        """Get notification delivery statistics"""
        return {
            "delivery_stats": self._delivery_stats.copy(),
            "queue_size": len(self._notification_queue),
            "pending_notifications": len([n for n in self._notification_queue if n.sent_at is None]),
            "channels_available": list(self._channel_handlers.keys())
        }
