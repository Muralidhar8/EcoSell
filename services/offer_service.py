from decimal import Decimal
from datetime import datetime
from models import db, SellingTicket, BuyerOffer, Pickup, User
from services.notification_service import NotificationService

class OfferService:
    @staticmethod
    def submit_or_update_offer(buyer_id, ticket_id, offered_price_per_kg):
        """Submit a new offer or update existing offer on an open ticket."""
        ticket = SellingTicket.query.get(ticket_id)
        if not ticket:
            return False, "Ticket not found."
        
        if ticket.status != 'Open':
            return False, "This ticket is no longer open for offers."
        
        if ticket.seller_id == buyer_id:
            return False, "You cannot make an offer on your own garbage ticket."
        
        buyer = User.query.get(buyer_id)
        if not buyer or not buyer.is_verified_buyer:
            return False, "Only verified buyers can submit price offers."

        price = Decimal(str(offered_price_per_kg))
        if price <= 0:
            return False, "Offered price must be greater than zero."

        estimated_total = Decimal(str(ticket.estimated_quantity)) * price

        # Check existing offer by this buyer on this ticket
        existing_offer = BuyerOffer.query.filter_by(ticket_id=ticket_id, buyer_id=buyer_id).first()
        if existing_offer:
            if existing_offer.offer_status not in ['Pending', 'Withdrawn']:
                return False, f"Offer cannot be modified in its current state ({existing_offer.offer_status})."
            existing_offer.offered_price_per_kg = price
            existing_offer.estimated_total = estimated_total
            existing_offer.offer_status = 'Pending'
            existing_offer.created_at = datetime.utcnow()
            offer = existing_offer
        else:
            offer = BuyerOffer(
                ticket_id=ticket_id,
                buyer_id=buyer_id,
                offered_price_per_kg=price,
                estimated_total=estimated_total,
                offer_status='Pending'
            )
            db.session.add(offer)

        db.session.commit()

        # Notify seller
        shop_name = buyer.buyer_profile.shop_name if buyer.buyer_profile else buyer.full_name
        NotificationService.send(
            user_id=ticket.seller_id,
            title="New Price Offer Received",
            message=f"{shop_name} offered ₹{price:.2f}/kg (Est. Total: ₹{estimated_total:.2f}) on ticket {ticket.ticket_number}."
        )

        return True, "Offer submitted successfully!"

    @staticmethod
    def withdraw_offer(buyer_id, offer_id):
        """Buyer withdraws pending offer."""
        offer = BuyerOffer.query.filter_by(id=offer_id, buyer_id=buyer_id).first()
        if not offer:
            return False, "Offer not found."
        if offer.offer_status != 'Pending':
            return False, "Only pending offers can be withdrawn."
        
        offer.offer_status = 'Withdrawn'
        db.session.commit()
        return True, "Offer withdrawn successfully."

    @staticmethod
    def accept_offer(seller_id, offer_id):
        """Seller accepts a buyer's offer. Enforces safe transaction and concurrency rules."""
        # Use database transaction
        try:
            offer = BuyerOffer.query.get(offer_id)
            if not offer:
                return False, "Offer not found."

            ticket = SellingTicket.query.filter_by(id=offer.ticket_id, seller_id=seller_id).first()
            if not ticket:
                return False, "Unauthorized: Ticket does not belong to you."

            if ticket.status != 'Open':
                return False, f"Ticket cannot be accepted because its status is already '{ticket.status}'."

            if offer.offer_status != 'Pending':
                return False, f"This offer is currently '{offer.offer_status}' and cannot be accepted."

            # Verify buyer is still verified
            buyer = User.query.get(offer.buyer_id)
            if not buyer or not buyer.is_verified_buyer:
                return False, "Selected buyer is not currently verified to collect garbage."

            # 1. Accept this offer
            offer.offer_status = 'Accepted'

            # 2. Reject/Close all other offers on this ticket
            other_offers = BuyerOffer.query.filter(
                BuyerOffer.ticket_id == ticket.id,
                BuyerOffer.id != offer.id,
                BuyerOffer.offer_status == 'Pending'
            ).all()
            for other in other_offers:
                other.offer_status = 'Closed'

            # 3. Update ticket status
            ticket.status = 'Offer Accepted'

            # 4. Create Pickup record
            pickup = Pickup.query.filter_by(ticket_id=ticket.id).first()
            if not pickup:
                pickup = Pickup(
                    ticket_id=ticket.id,
                    buyer_id=buyer.id,
                    seller_id=seller_id,
                    pickup_date=ticket.preferred_pickup_date,
                    pickup_time=ticket.preferred_pickup_time,
                    pickup_status='Scheduled'
                )
                db.session.add(pickup)
            else:
                pickup.buyer_id = buyer.id
                pickup.pickup_status = 'Scheduled'
                pickup.pickup_date = ticket.preferred_pickup_date
                pickup.pickup_time = ticket.preferred_pickup_time

            db.session.commit()

            # 5. Send notifications
            NotificationService.send(
                user_id=buyer.id,
                title="Offer Accepted! Pickup Scheduled",
                message=f"Seller accepted your offer of ₹{offer.offered_price_per_kg:.2f}/kg for ticket {ticket.ticket_number}. Pickup is scheduled for {ticket.preferred_pickup_date} ({ticket.preferred_pickup_time})."
            )
            NotificationService.send(
                user_id=seller_id,
                title="Offer Accepted",
                message=f"You accepted {buyer.buyer_profile.shop_name if buyer.buyer_profile else buyer.full_name}'s offer for ticket {ticket.ticket_number}."
            )

            return True, "Offer accepted successfully! Pickup has been scheduled."
        except Exception as e:
            db.session.rollback()
            return False, f"Error processing offer acceptance: {str(e)}"

