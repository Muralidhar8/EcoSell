from datetime import datetime
from models import db, SellingTicket, Notification
from services.notification_service import NotificationService

class TicketService:
    @staticmethod
    def generate_ticket_number():
        """Generate ticket number format: GARB-YYYY-XXXX (e.g., GARB-2026-0001)."""
        current_year = datetime.utcnow().year
        prefix = f"GARB-{current_year}-"
        
        # Get count of tickets created this year
        count = SellingTicket.query.filter(SellingTicket.ticket_number.like(f"{prefix}%")).count()
        next_seq = count + 1
        
        # Ensure uniqueness in case of gaps
        while True:
            candidate = f"{prefix}{next_seq:04d}"
            exists = SellingTicket.query.filter_by(ticket_number=candidate).first()
            if not exists:
                return candidate
            next_seq += 1

    @staticmethod
    def create_ticket(seller_id, category_id, estimated_quantity, garbage_condition,
                      description, pickup_address, city, pincode,
                      preferred_pickup_date, preferred_pickup_time, image_filename=None):
        ticket_number = TicketService.generate_ticket_number()
        ticket = SellingTicket(
            ticket_number=ticket_number,
            seller_id=seller_id,
            category_id=category_id,
            estimated_quantity=estimated_quantity,
            unit='kg',
            garbage_condition=garbage_condition,
            description=description,
            image=image_filename,
            pickup_address=pickup_address,
            city=city,
            pincode=pincode,
            preferred_pickup_date=preferred_pickup_date,
            preferred_pickup_time=preferred_pickup_time,
            status='Open'
        )
        db.session.add(ticket)
        db.session.commit()

        # Send notification to seller
        NotificationService.send(
            user_id=seller_id,
            title="Garbage Ticket Created",
            message=f"Your ticket {ticket_number} has been created and is now visible to verified scrap dealers."
        )
        return ticket

