from decimal import Decimal
from datetime import datetime
from models import db, SellingTicket, BuyerOffer, Pickup, Transaction, User
from services.notification_service import NotificationService

class PaymentService:
    @staticmethod
    def complete_collection_and_payment(buyer_id, ticket_id, actual_weight, payment_method, collection_notes=None):
        """
        Record actual weight, finalize payment based on accepted rate, 
        complete pickup, create permanent transaction record, and update ticket status.
        """
        try:
            ticket = SellingTicket.query.get(ticket_id)
            if not ticket:
                return False, "Ticket not found."

            pickup = Pickup.query.filter_by(ticket_id=ticket.id).first()
            if not pickup:
                return False, "Pickup record not found for this ticket."

            if pickup.buyer_id != buyer_id:
                return False, "Unauthorized: You are not the assigned buyer for this pickup."

            if ticket.status == 'Completed':
                return False, "This transaction has already been completed."

            # Find accepted offer to get the accepted price per kg
            accepted_offer = BuyerOffer.query.filter_by(
                ticket_id=ticket.id,
                buyer_id=buyer_id,
                offer_status='Accepted'
            ).first()

            if not accepted_offer:
                return False, "No accepted offer found for this buyer on this ticket."

            act_weight = Decimal(str(actual_weight))
            if act_weight <= 0:
                return False, "Actual collected weight must be greater than zero."

            price_per_kg = Decimal(str(accepted_offer.offered_price_per_kg))
            total_amount = round(act_weight * price_per_kg, 2)

            now = datetime.utcnow()

            # 1. Update Pickup
            pickup.actual_weight = act_weight
            pickup.pickup_status = 'Completed'
            pickup.completed_at = now
            if collection_notes:
                pickup.collection_notes = collection_notes

            # 2. Create or Update Transaction
            transaction = Transaction.query.filter_by(ticket_id=ticket.id).first()
            if not transaction:
                transaction = Transaction(
                    ticket_id=ticket.id,
                    buyer_id=buyer_id,
                    seller_id=ticket.seller_id,
                    actual_weight=act_weight,
                    price_per_kg=price_per_kg,
                    total_amount=total_amount,
                    payment_method=payment_method if payment_method in ['Cash', 'UPI', 'Online'] else 'Cash',
                    payment_status='Completed',
                    transaction_date=now
                )
                db.session.add(transaction)
            else:
                transaction.actual_weight = act_weight
                transaction.price_per_kg = price_per_kg
                transaction.total_amount = total_amount
                transaction.payment_method = payment_method
                transaction.payment_status = 'Completed'
                transaction.transaction_date = now

            # 3. Update Ticket status
            ticket.status = 'Completed'

            db.session.commit()

            # 4. Notify both parties
            buyer = User.query.get(buyer_id)
            shop_name = buyer.buyer_profile.shop_name if (buyer and buyer.buyer_profile) else "Scrap Dealer"
            
            NotificationService.send(
                user_id=ticket.seller_id,
                title=f"Garbage Collected & Paid ₹{total_amount:.2f}",
                message=f"{shop_name} completed pickup for ticket {ticket.ticket_number}. Actual weight: {act_weight} kg @ ₹{price_per_kg}/kg = ₹{total_amount:.2f} via {payment_method}."
            )

            NotificationService.send(
                user_id=buyer_id,
                title=f"Collection & Payment Recorded (₹{total_amount:.2f})",
                message=f"Pickup for ticket {ticket.ticket_number} marked completed. Total paid: ₹{total_amount:.2f}."
            )

            return True, f"Collection & Payment completed successfully! Total amount: ₹{total_amount:.2f}"
        except Exception as e:
            db.session.rollback()
            return False, f"Payment completion failed: {str(e)}"

