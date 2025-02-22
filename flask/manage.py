from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from app import app, db
from app.models.contact import Contact
from app.models.jubjai import User,Category,Expense
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
        description="Expenses on food and dining",
        monthly_limit=500.00,
        user_id=user.id,
    )
    # Set the foreign key (category.user_id) to the created user's id
    db.session.add(category)
    db.session.commit()  # Commit to get category.category_id generated

    # Create a sample expense for the user in the created category
    expense = Expense(
        amount=100.00,
        entry_method="manual",  # Only "manual" or "slip" allowed
        description="Lunch at a restaurant",
        expense_date=datetime.now(),
        user_id=user.id,
        category_id=category.category_id
    )
    # Set foreign keys for expense
    db.session.add(expense)
    db.session.commit()





if __name__ == "__main__":
    cli()