from models import db, Notification

class NotificationService:
    @staticmethod
    def send(user_id, title, message):
        """Create and persist a new notification for a user."""
        try:
            notif = Notification(user_id=user_id, title=title, message=message)
            db.session.add(notif)
            db.session.commit()
            return notif
        except Exception as e:
            db.session.rollback()
            print(f"Error creating notification: {e}")
            return None

    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark a notification as read if it belongs to the user."""
        notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notif:
            notif.is_read = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications of a user as read."""
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return True

    @staticmethod
    def get_unread_count(user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

