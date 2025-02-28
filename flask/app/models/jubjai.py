from flask_login import UserMixin
from datetime import datetime, timedelta
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
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, email, name, password, avatar_url, id=None,date_created=None, date_updated=None, is_deleted=False, is_admin=False):
        if is_admin:
            self.id = 0
        else:
            self.id = id
        self.email = email
        self.name = name
        self.password = password
        self.avatar_url = avatar_url
        self.date_created = date_created if date_created else datetime.now()
        self.date_updated = date_updated if date_updated else datetime.now()
        self.is_deleted = is_deleted
        self.is_admin = is_admin

class Category(db.Model, SerializerMixin):
    __tablename__ = "categories"
    # Exclude the 'category' attribute inside each transactions to prevent recursion.
    __serialize_rules__ = ['-user', '-transactions.category', '-transactions.user']
    category_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    icon_url = db.Column(db.String)
    monthly_limit = db.Column(db.Numeric(10, 2))
    transaction_type = db.Column(
        Enum('income', 'expense', name='category_type_enum'),
        nullable=False
    )
    is_deleted = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, name, user_id, icon_url,transaction_type,description=None, monthly_limit=None, date_created=None, date_updated=None, is_deleted=False):
        self.name = name
        self.description = description
        self.transaction_type = transaction_type
        self.icon_url = icon_url
        self.user_id = user_id
        self.monthly_limit = monthly_limit
        self.date_created = date_created if date_created else datetime.now()
        self.date_updated = date_updated if date_updated else datetime.now()
        self.is_deleted = is_deleted

class Transaction(db.Model, SerializerMixin):
    __tablename__ = "transactions"
    # Exclude the reverse relationship fields to break recursion
    __serialize_rules__ = ['-category.transactions', '-user.transactions']
    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.category_id"), nullable=False)
    transaction_date = db.Column(db.Date)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String)
    transaction_type = db.Column(Enum('income', 'expense', name='transaction_type_enum'), nullable=False)
    entry_method = db.Column(Enum('manual', 'slip', name='entry_method_enum'), nullable=False)
    slip_image_url = db.Column(db.String)
    is_deleted = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
        
    def __init__(self, amount, entry_method, user_id, category_id, transaction_type, slip_image_url=None, description=None, transaction_date=None, date_created=None, date_updated=None, is_deleted=False):
        self.transaction_date = transaction_date
        self.amount = amount
        self.description = description
        self.user_id = user_id
        self.category_id = category_id
        self.transaction_type = transaction_type
        if entry_method not in ['manual', 'slip']:
            raise ValueError("entry_method must be either 'manual' or 'slip'")
        self.entry_method = entry_method
        self.slip_image_url = slip_image_url
        self.date_created = date_created if date_created else datetime.now()
        self.date_updated = date_updated if date_updated else datetime.now()
        self.is_deleted = is_deleted

class Budget(db.Model, SerializerMixin):
    __tablename__="budgets"
    __serialize_rules__=['-user', '-category.transactions', '-category.user']
    budget_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.category_id"), nullable=False)
    month = db.Column(db.String(7), nullable=False)
    monthly_limit = db.Column(db.Numeric(10, 2), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_deleted = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, category_id, month, date_created=None, date_updated=None, is_deleted=False):
        self.user_id = user_id
        self.category_id = category_id
        self.month = month

        category = Category.query.filter_by(category_id=category_id, user_id=user_id).first()
        if not category or category.monthly_limit is None or category.monthly_limit <= 0:
            raise ValueError("Invalid category or monthly limit")
        
        self.monthly_limit = category.monthly_limit
        
        start_date = datetime.strptime(month, "%Y-%m")
        end_date = datetime(start_date.year, start_date.month + 1, 1) if start_date.month < 12 else datetime(start_date.year + 1, 1, 1)

        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.category_id == category_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date,
            Transaction.transaction_type == 'expense',
            Transaction.is_deleted == False
        ).all()

        self.amount = sum(t.amount or 0 for t in transactions)
        self.date_created = date_created if date_created else datetime.now()
        self.date_updated = date_updated if date_updated else datetime.now()
        self.is_deleted = is_deleted







    



