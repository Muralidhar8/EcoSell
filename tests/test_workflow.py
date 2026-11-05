import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from decimal import Decimal
from datetime import date, timedelta
from app import create_app, seed_initial_data
from models import db, User, SellingTicket, BuyerOffer, Pickup, Transaction, BuyerPrice, GarbageCategory

class EcoSellWorkflowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed categories & default admin/users
        seed_initial_data(self.app)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_01_landing_page(self):
        """Test landing page renders with EcoSell branding and categories."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'EcoSell', response.data)
        self.assertIn(b'Turn Your Waste', response.data)
        self.assertIn(b'Plastic', response.data)
        self.assertIn(b'Copper', response.data)

    def test_02_seller_registration_and_login(self):
        """Test new seller registration and login."""
        response = self.client.post('/register/seller', data={
            'full_name': 'Test New Seller',
            'email': 'newseller@example.com',
            'phone': '+91 9111122223',
            'password': 'password123',
            'confirm_password': 'password123',
            'address': 'Plot 44, Hill Road, Bandra',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400050'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(email='newseller@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'seller')
        self.assertIsNotNone(user.seller_profile)
        self.assertEqual(user.seller_profile.city, 'Mumbai')

    def test_03_buyer_registration(self):
        """Test new buyer registration with pending status."""
        response = self.client.post('/register/buyer', data={
            'full_name': 'Test Scrap Dealer',
            'email': 'newbuyer@example.com',
            'phone': '+91 9333344445',
            'password': 'password123',
            'confirm_password': 'password123',
            'shop_name': 'Sunrise Recyclers',
            'shop_address': 'Shop 1, Link Road, Goregaon',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400062',
            'service_area': 'Goregaon, Malad, Kandivali'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        buyer = User.query.filter_by(email='newbuyer@example.com').first()
        self.assertIsNotNone(buyer)
        self.assertEqual(buyer.role, 'buyer')
        self.assertEqual(buyer.buyer_profile.verification_status, 'pending')

    def test_04_full_marketplace_lifecycle(self):
        """
        Test the entire end-to-end scenario:
        1. Seller logs in and creates a garbage selling ticket.
        2. Buyer logs in, browses tickets, views ticket details and places a price bid.
        3. Competing buyer places another bid.
        4. Seller compares offers and accepts the winning bid.
        5. System rejects/closes other bids and schedules pickup.
        6. Buyer updates pickup status and records actual verified weight & payment.
        7. Final amount is calculated accurately (Actual Weight * Rate).
        8. Permanent transaction record is verified.
        """
        # Step 1: Seller login and create ticket
        self.login('seller@ecosell.com', 'password123')
        pickup_date = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
        res_create = self.client.post('/seller/tickets/create', data={
            'category_id': 1,  # Plastic
            'estimated_quantity': '30.0',
            'garbage_condition': 'Sorted',
            'description': 'Sorted PET and HDPE bottles rinsed and packed in sacks.',
            'pickup_address': 'Flat 402, Green Meadows Apartment, MG Road',
            'city': 'Mumbai',
            'pincode': '400001',
            'preferred_pickup_date': pickup_date,
            'preferred_pickup_time': '11:00 AM - 01:00 PM'
        }, follow_redirects=True)
        self.assertEqual(res_create.status_code, 200)

        ticket = SellingTicket.query.filter_by(seller_id=2, estimated_quantity=30.0).first()
        self.assertIsNotNone(ticket)
        self.assertTrue(ticket.ticket_number.startswith('GARB-'))
        self.assertEqual(ticket.status, 'Open')
        self.logout()

        # Step 2: Buyer 1 (Amit Patel) places bid @ Rs 15.00/kg
        self.login('buyer1@ecosell.com', 'password123')
        res_bid1 = self.client.post(f'/buyer/tickets/{ticket.id}/offer', data={
            'offered_price_per_kg': '15.00'
        }, follow_redirects=True)
        self.assertEqual(res_bid1.status_code, 200)

        offer1 = BuyerOffer.query.filter_by(ticket_id=ticket.id, buyer_id=3).first()
        self.assertIsNotNone(offer1)
        self.assertEqual(float(offer1.offered_price_per_kg), 15.00)
        self.assertEqual(float(offer1.estimated_total), 450.00)
        self.logout()

        # Step 3: Buyer 2 (Priya Verma) places competing bid @ Rs 16.50/kg
        self.login('buyer2@ecosell.com', 'password123')
        res_bid2 = self.client.post(f'/buyer/tickets/{ticket.id}/offer', data={
            'offered_price_per_kg': '16.50'
        }, follow_redirects=True)
        self.assertEqual(res_bid2.status_code, 200)

        offer2 = BuyerOffer.query.filter_by(ticket_id=ticket.id, buyer_id=4).first()
        self.assertIsNotNone(offer2)
        self.assertEqual(float(offer2.offered_price_per_kg), 16.50)
        self.assertEqual(float(offer2.estimated_total), 495.00)
        self.logout()

        # Step 4: Seller logs in, compares offers, and accepts Buyer 2's offer (highest bid)
        self.login('seller@ecosell.com', 'password123')
        res_accept = self.client.post(f'/seller/offers/{offer2.id}/accept', follow_redirects=True)
        self.assertEqual(res_accept.status_code, 200)

        # Reload objects from DB
        db.session.expire_all()
        ticket = SellingTicket.query.get(ticket.id)
        offer1 = BuyerOffer.query.get(offer1.id)
        offer2 = BuyerOffer.query.get(offer2.id)

        self.assertEqual(ticket.status, 'Offer Accepted')
        self.assertEqual(offer2.offer_status, 'Accepted')
        self.assertEqual(offer1.offer_status, 'Closed')  # Competing offer automatically closed!

        pickup = Pickup.query.filter_by(ticket_id=ticket.id).first()
        self.assertIsNotNone(pickup)
        self.assertEqual(pickup.buyer_id, 4)
        self.assertEqual(pickup.pickup_status, 'Scheduled')
        self.logout()

        # Step 5: Buyer 2 visits seller, updates transit status
        self.login('buyer2@ecosell.com', 'password123')
        res_transit = self.client.post(f'/buyer/pickups/{pickup.id}/status', data={
            'pickup_status': 'Arrived'
        }, follow_redirects=True)
        self.assertEqual(res_transit.status_code, 200)

        pickup = Pickup.query.get(pickup.id)
        self.assertEqual(pickup.pickup_status, 'Arrived')

        # Step 6: Buyer 2 physically weighs the scrap on digital scale: Actual weight is 32.5 kg
        # Final amount = 32.5 kg * Rs 16.50 = Rs 536.25
        res_pay = self.client.post(f'/buyer/pickups/{pickup.id}/complete', data={
            'actual_weight': '32.5',
            'payment_method': 'UPI',
            'collection_notes': 'Clean PET bottles verified on digital scale.'
        }, follow_redirects=True)
        self.assertEqual(res_pay.status_code, 200)

        # Verify completed transaction and ticket status
        db.session.expire_all()
        ticket = SellingTicket.query.get(ticket.id)
        pickup = Pickup.query.get(pickup.id)
        transaction = Transaction.query.filter_by(ticket_id=ticket.id).first()

        self.assertEqual(ticket.status, 'Completed')
        self.assertEqual(pickup.pickup_status, 'Completed')
        self.assertEqual(float(pickup.actual_weight), 32.5)

        self.assertIsNotNone(transaction)
        self.assertEqual(float(transaction.actual_weight), 32.5)
        self.assertEqual(float(transaction.price_per_kg), 16.50)
        self.assertEqual(float(transaction.total_amount), 536.25)
        self.assertEqual(transaction.payment_method, 'UPI')
        self.assertEqual(transaction.payment_status, 'Completed')
        self.logout()

        # Step 7: Seller logs in and submits a 5-star review for the buyer
        self.login('seller@ecosell.com', 'password123')
        res_rev = self.client.post(f'/seller/reviews/submit/{ticket.id}', data={
            'rating': '5',
            'review_text': 'Punctual collection and seamless UPI payout!'
        }, follow_redirects=True)
        self.assertEqual(res_rev.status_code, 200)
        self.logout()

if __name__ == '__main__':
    unittest.main()
