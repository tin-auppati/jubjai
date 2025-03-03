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
    category_food = Category(
        name="Food",
        user_id=user.id,
        icon_url="https://cdn-icons-png.flaticon.com/512/1046/1046857.png",
        # description="Transactions on food and dining",
        transaction_type="expense",
        # limit=500.00 # if want limit
    )
    
    db.session.add(category_food)
    db.session.commit() 

    # Create a sample category for the user
    category_shopping = Category(
        name="Shopping",
        user_id=user.id,
        icon_url="https://cdn-icons-png.flaticon.com/512/3081/3081415.png",
        # description="",
        transaction_type="expense",
        # limit=500.00 # if want limit
    )
    
    db.session.add(category_shopping)
    db.session.commit() 

    # Create a sample category for the user
    category_billing = Category(
        name="Pay the bill",
        user_id=user.id,
        icon_url="https://cdn-icons-png.flaticon.com/512/8583/8583679.png",
        # description="",
        transaction_type="expense",
        # limit=500.00 # if want limit
    )
    
    db.session.add(category_billing)
    db.session.commit() 

    # Create a sample category for the user
    category_gift = Category(
        name="Gift",
        user_id=user.id,
        icon_url="https://cdn-icons-png.flaticon.com/512/1139/1139931.png",
        # description="",
        transaction_type="expense",
        # limit=500.00 # if want limit
    )
    
    db.session.add(category_gift)
    db.session.commit() 

    # Create a sample category for the user
    category_travel = Category(
        name="Travel",
        user_id=user.id,
        icon_url="https://cdn-icons-png.flaticon.com/512/9482/9482066.png",
        # description="",
        transaction_type="expense",
        # limit=500.00 # if want limit
    )
    
    db.session.add(category_travel)
    db.session.commit() 

    # ----------------------------------------------------------

    category_income = Category(
        name="Income",
        user_id=user.id,
        transaction_type = "income",
        icon_url="https://cdn-icons-png.flaticon.com/512/2871/2871405.png",
        # description="Income",
    )
    
    db.session.add(category_income)
    db.session.commit()  

    category_money_saving = Category(
        name="Money Saving",
        user_id=user.id,
        transaction_type = "income",
        icon_url="https://cdn-icons-png.flaticon.com/512/9018/9018937.png",
        # description="Income",
    )
    
    db.session.add(category_money_saving)
    db.session.commit()

    # ----------------------------------------------------------

    
    transaction = Transaction(
        amount=100.00,
        entry_method="manual",  # Only "manual" or "slip" allowed
        description="Lunch at a restaurant",
        transaction_date=datetime.now(),
        user_id=user.id,
        category_id=category_food.category_id,
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