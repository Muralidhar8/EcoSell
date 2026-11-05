from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .seller import SellerProfile
from .buyer import BuyerProfile
from .category import GarbageCategory
from .ticket import SellingTicket
from .offer import BuyerPrice, BuyerOffer
from .pickup import Pickup
from .transaction import Transaction
from .review import Review
from .complaint import Complaint
from .notification import Notification

__all__ = [
    'db',
    'User',
    'SellerProfile',
    'BuyerProfile',
    'GarbageCategory',
    'SellingTicket',
    'BuyerPrice',
    'BuyerOffer',
    'Pickup',
    'Transaction',
    'Review',
    'Complaint',
    'Notification'
]

