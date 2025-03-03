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

    
    # Create a sample category for the user
    category = Category(
        name="Food",
        user_id=user.id,
        icon_url="https://cdn-icons-png.flaticon.com/512/1046/1046857.png",
        description="Transactions on food and dining",
        transaction_type="expense",
        limit=500.00
    )
    
    db.session.add(category)
    db.session.commit()  

    category_income = Category(
        name="Income",
        user_id=user.id,
        transaction_type = "income",
        icon_url="https://cdn-icons-png.flaticon.com/512/123/123123.png",
        description="Income",
    )
    
    db.session.add(category_income)
    db.session.commit()  

    
    transaction = Transaction(
        amount=100.00,
        entry_method="manual",  # Only "manual" or "slip" allowed
        description="Lunch at a restaurant",
        transaction_date=datetime.now(),
        user_id=user.id,
        category_id=category.category_id,
        transaction_type = "expense"
    )
    
    db.session.add(transaction)
    db.session.commit()

    transaction_income = Transaction(
        amount=100.00,
        entry_method="manual",  # Only "manual" or "slip" allowed
        description="Income",
        transaction_date=datetime.now(),
        user_id=user.id,
        category_id=category_income.category_id,
        transaction_type = "income"
    )
    
    db.session.add(transaction_income)
    db.session.commit()




if __name__ == "__main__":
    cli()