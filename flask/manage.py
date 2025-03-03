from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from app import app, db
from app.models.jubjai import User,Category,Transaction
from app import views
from datetime import datetime


cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.reflect()
    db.drop_all()
    db.create_all()
    db.session.commit()

def create_default_categories_for_user(user):
    
    default_categories = [
        {
            "name": "Food",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/1046/1046857.png",
            "transaction_type": "expense"
        },
        {
            "name": "Shopping",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/3081/3081415.png",
            "transaction_type": "expense"
        },
        {
            "name": "Pay the bill",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/8583/8583679.png",
            "transaction_type": "expense"
        },
        {
            "name": "Gift",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/1139/1139931.png",
            "transaction_type": "expense"
        },
        {
            "name": "Travel",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/9482/9482066.png",
            "transaction_type": "expense"
        },
        {
            "name": "Income",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/2871/2871405.png",
            "transaction_type": "income"
        },
        {
            "name": "Money Saving",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/9018/9018937.png",
            "transaction_type": "income"
        }
    ]
    
    for cat in default_categories:
        # Check if the category already exists for the user
        if not Category.query.filter_by(user_id=user.id, name=cat["name"]).first():
            new_category = Category(
                name=cat["name"],
                user_id=user.id,
                icon_url=cat["icon_url"],
                transaction_type=cat["transaction_type"]
            )
            db.session.add(new_category)
    db.session.commit()



@cli.command("seed_db")
def seed_db():
    admin = User(
        id=0,
        email="admin@example.com",
        name="Admin User",
        password=generate_password_hash('adminpass', method='sha256'),
        avatar_url="https://ui-avatars.com/api/?name=Admin&background=000&color=fff",
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()

    user = User(
        email="flask@204212",
        name='สมชาย ทรงแบด',
        password=generate_password_hash('1234', method='sha256'),
        avatar_url=("https://ui-avatars.com/api/"
                    "?name=สมชาย+ทรงแบด"
                    "&background=83ee03&color=fff"),
    )
    db.session.add(user)
    db.session.commit()
    
    # Add default categories for this user
    create_default_categories_for_user(user)

    # Optionally, add other seed data (transactions, etc.)
    transaction = Transaction(
        amount=100.00,
        entry_method="manual",  # Only "manual" or "slip" allowed
        description="Lunch at a restaurant",
        transaction_date=datetime.now(),
        user_id=user.id,
        category_id=Category.query.filter_by(user_id=user.id, name="Food").first().category_id,
        transaction_type="expense"
    )
    db.session.add(transaction)
    db.session.commit()

    transaction_income = Transaction(
        amount=100.00,
        entry_method="manual",
        description="Income",
        transaction_date=datetime.now(),
        user_id=user.id,
        category_id=Category.query.filter_by(user_id=user.id, name="Income").first().category_id,
        transaction_type="income"
    )
    db.session.add(transaction_income)
    db.session.commit()




if __name__ == "__main__":
    cli()