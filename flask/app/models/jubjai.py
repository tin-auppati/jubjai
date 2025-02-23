from flask_login import UserMixin
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin
from app import db
from sqlalchemy import Enum


class User(db.Model, UserMixin, SerializerMixin):
    __tablename__ = "users"
    __serialize_rules__ = ['-categories.user', '-expenses.user']
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    name = db.Column(db.String)
    password = db.Column(db.String)
    avatar_url = db.Column(db.String(300))
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_deleted = db.Column(db.Boolean, default=False)

    def __init__(self, email, name, password, avatar_url, date_created=None, date_updated=None, is_deleted=False):
        self.email = email
        self.name = name
        self.password = password
        self.avatar_url = avatar_url
        self.date_created = date_created if date_created else datetime.now()
        self.date_updated = date_updated if date_updated else datetime.now()
        self.is_deleted = is_deleted

class Category(db.Model, SerializerMixin):
    __tablename__ = "categories"
    # Exclude the 'category' attribute inside each expense to prevent recursion.
    __serialize_rules__ = ['-user', '-expenses.category', '-expenses.user']
    category_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    icon_url = db.Column(db.String)
    monthly_limit = db.Column(db.Numeric(10, 2))
    is_deleted = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, name, user_id, icon_url,description=None, monthly_limit=None, date_created=None, date_updated=None, is_deleted=False):
        self.name = name
        self.description = description
        self.icon_url = icon_url
        self.user_id = user_id
        self.monthly_limit = monthly_limit
        self.date_created = date_created if date_created else datetime.now()
        self.date_updated = date_updated if date_updated else datetime.now()
        self.is_deleted = is_deleted

class Expense(db.Model, SerializerMixin):
    __tablename__ = "expenses"
    # Exclude the reverse relationship fields to break recursion
    __serialize_rules__ = ['-category.expenses', '-user.expenses']
    expense_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.category_id"), nullable=False)
    expense_date = db.Column(db.Date)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String)
    entry_method = db.Column(Enum('manual', 'slip', name='entry_method_enum'), nullable=False)
    slip_image_url = db.Column(db.String)
    is_deleted = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __init__(self, amount, entry_method, user_id, category_id,slip_image_url=None, description=None, expense_date=None, date_created=None, date_updated=None, is_deleted=False):
        self.expense_date = expense_date
        self.amount = amount
        self.description = description
        self.user_id = user_id
        self.category_id = category_id
        if entry_method not in ['manual', 'slip']:
            raise ValueError("entry_method must be either 'manual' or 'slip'")
        self.entry_method = entry_method
        self.slip_image_url = slip_image_url
        self.date_created = date_created if date_created else datetime.now()
        self.date_updated = date_updated if date_updated else datetime.now()
        self.is_deleted = is_deleted

