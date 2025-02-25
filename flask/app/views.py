import json
import secrets
import string
from flask import (jsonify, render_template,
                  request, url_for, flash, redirect, current_app)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from sqlalchemy.sql import text
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from app import app
from app import db
from app import login_manager
from app import oauth
from datetime import datetime
from decimal import Decimal
import os

from app.models.contact import Contact
from app.models.jubjai import User,Category,Expense
from flask import send_from_directory


@app.route('/')
def home():
    return "Flask says 'Hello world!'"

@app.route('/crash')
def crash():
    return 1/0

@app.route('/verify-tessdata')
def verify_tessdata():
    return app.send_static_file('tessdata/tha.traineddata')


@app.route('/db')
def db_connection():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return '<h1>db works.</h1>'
    except Exception as e:
        return '<h1>db is broken.</h1>' + str(e)


@app.route('/jubjai_users_db')
def view_jubjai_users():
        
    query = User.query
    is_deleted_param = request.args.get('is_deleted')
    if is_deleted_param is not None:
        # Convert the parameter to a boolean.
        if is_deleted_param.lower() in ('true', '1', 'yes'):
            is_deleted_value = True
        else:
            is_deleted_value = False
        query = query.filter_by(is_deleted=is_deleted_value)

    # Optional ordering: default is descending by date_updated.
    order = request.args.get('order', 'desc').lower()
    if order == 'asc':
        query = query.order_by(User.date_updated.asc())
    else:
        query = query.order_by(User.date_updated.desc())

    users = query.all()
    entries_json = [entry.to_dict() for entry in users]
    return jsonify(entries_json)

@app.route('/jubjai_catagories_db')
def view_jubjai_catagories():
        
    query = Category.query
    is_deleted_param = request.args.get('is_deleted')
    if is_deleted_param is not None:
        # Convert the parameter to a boolean.
        if is_deleted_param.lower() in ('true', '1', 'yes'):
            is_deleted_value = True
        else:
            is_deleted_value = False
        query = query.filter_by(is_deleted=is_deleted_value)

    # Optional ordering: default is descending by date_updated.
    order = request.args.get('order', 'desc').lower()
    if order == 'asc':
        query = query.order_by(Category.date_updated.asc())
    else:
        query = query.order_by(Category.date_updated.desc())

    users = query.all()
    entries_json = [entry.to_dict() for entry in users]
    return jsonify(entries_json)

@app.route('/jubjai_expenses_db')
def view_jubjai_expenses():
        
    query = Expense.query
    is_deleted_param = request.args.get('is_deleted')
    if is_deleted_param is not None:
        # Convert the parameter to a boolean.
        if is_deleted_param.lower() in ('true', '1', 'yes'):
            is_deleted_value = True
        else:
            is_deleted_value = False
        query = query.filter_by(is_deleted=is_deleted_value)

    # Optional ordering: default is descending by date_updated.
    order = request.args.get('order', 'desc').lower()
    if order == 'asc':
        query = query.order_by(Expense.date_updated.asc())
    else:
        query = query.order_by(Expense.date_updated.desc())

    users = query.all()
    entries_json = [entry.to_dict() for entry in users]
    return jsonify(entries_json)



@app.route('/users')
def users_index():
   return render_template('users/index.html')


@app.route('/users/profile')
@login_required
def users_profile():
    profile_image = current_user.avatar_url
    return render_template('users/profile.html', profile_image=profile_image)

@app.route('/users/upload_profile', methods=['POST'])
@login_required
def upload_profile():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # update avatar_url in db
        current_user.avatar_url = url_for('static', filename=f'uploads/{filename}')
        db.session.commit()

        flash('Profile image updated!')
        return redirect(url_for('users_profile'))
    else:
        flash('File type not allowed!')
        return redirect(url_for('users_profile'))


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our
    # user table, use it in the query for the user
    return User.query.get(int(user_id))

@app.route('/users/login', methods=('GET', 'POST'))
def users_login():
    if current_user and current_user.is_authenticated:
        return redirect(url_for('users_profile'))


    if request.method == 'POST':
        if request.is_json:
            input_ = request.json
        else:
           input_ = request.form.to_dict()
        # login code goes here
        email = input_.get('email')
        password = input_.get('password')
        remember = bool(input_.get('remember'))


        user = User.query.filter_by(email=email).first()
 
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the
        # hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Invalid login credentials')
            # if the user doesn't exist or password is wrong, reload the page
            return redirect(url_for('users_login'))


        # if the above check passes, then we know the user has the right
        # credentials
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('users_profile')
        return redirect(next_page)



    return render_template('users/login.html')


@app.route('/users/signup', methods=('GET', 'POST'))
def users_signup():
   if current_user and current_user.is_authenticated:
       return redirect(url_for('users_profile'))


   if request.method == 'POST':
       if request.is_json:
           result = request.json
       else:
           result = request.form.to_dict()


       app.logger.debug(str(result))


       
       validated_dict = {}
       valid_keys = ['email', 'name', 'password']


       # validate the input
       for key in valid_keys:
           app.logger.debug(str(key)+": " + str(result[key]))


           value = result[key].strip()
           if not value or value == 'undefined':
               break
           validated_dict[key] = value
           # code to validate and add user to database goes here
       app.logger.debug("validation done")


       if len(validated_dict.keys()) == len(valid_keys):
           app.logger.debug('validated dict: ' + str(validated_dict))
           email = validated_dict['email']
           name = validated_dict['name']
           password = validated_dict['password']
           try:
               with db.session.begin():  # Starts an explicit transaction
                   user = (User.query.filter_by(email=email)
                           .with_for_update().first())


                   if user:
                       flash('Email address already exists')
                       return redirect(url_for('users_signup'))


                   app.logger.debug("preparing to add")
                   avatar_url = gen_avatar_url(email, name)
                   hashed_password = generate_password_hash(password,
                                                            method='sha256')
                   new_user = User(email=email, name=name,
                                       password=hashed_password,
                                       avatar_url=avatar_url)
                   db.session.add(new_user)
                   return redirect(url_for('users_login'))
           # Transaction is committed when exiting the 'with' block
           except Exception as ex:
               db.session.rollback()  # Rollback on failure
               app.logger.error(f"Adding failed with email {email}: {ex}")
               return redirect(url_for('users_signup'))
      
   return render_template('users/signup.html')





def gen_avatar_url(email, name):
    bgcolor = generate_password_hash(email, method='sha256')[-6:]
    color = hex(int('0xffffff', 0) -
                int('0x'+bgcolor, 0)).replace('0x', '')
    lname = ''
    temp = name.split()
    fname = temp[0][0]
    if len(temp) > 1:
        lname = temp[1][0]


    avatar_url = "https://ui-avatars.com/api/?name=" + \
        fname + "+" + lname + "&background=" + \
        bgcolor + "&color=" + color
    return avatar_url


@app.route('/users/logout')
@login_required
def users_logout():
    logout_user()
    return redirect(url_for('users_index'))

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our
    # user table, use it in the query for the user
    return User.query.get(int(user_id))


@app.route('/google')
def google():


    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


   # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)




@app.route('/google/auth')
def google_auth():
    token = oauth.google.authorize_access_token()
    app.logger.debug(str(token))


    userinfo = token['userinfo']
    app.logger.debug(" Google User " + str(userinfo))
    email = userinfo['email']
    user = User.query.filter_by(email=email).first()


    if not user:
        name = userinfo.get('given_name','') + " " + userinfo.get('family_name','')
        random_pass_len = 8
        password = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                          for i in range(random_pass_len))
        picture = userinfo['picture']
        new_user = User(email=email, name=name,
                           password=generate_password_hash(
                               password, method='sha256'),
                           avatar_url=picture)
        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter_by(email=email).first()
    login_user(user)
    return redirect('/lab10')

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        monthly_limit = request.form.get('monthly_limit')
        icon_url = request.form.get('icon_url')
        # Convert monthly_limit to Decimal if provided
        from decimal import Decimal
        try:
            monthly_limit = Decimal(monthly_limit) if monthly_limit else None
        except Exception as e:
            monthly_limit = None

        new_category = Category(
            name=name,
            user_id=current_user.id,  # Make sure the user is logged in
            description=description,
            monthly_limit=monthly_limit,
            icon_url=icon_url
        )
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('create_expenses'))
    else:
        # Create a list of icons (30 icons, for example)
        icon_list = [
            {"name": "Food", "url": "https://cdn-icons-png.flaticon.com/512/1046/1046857.png"},
            {"name": "Travel", "url": "https://cdn-icons-png.flaticon.com/512/2922/2922510.png"},
            {"name": "Shopping", "url": "https://cdn-icons-png.flaticon.com/512/1041/1041914.png"},
            {"name": "Health", "url": "https://cdn-icons-png.flaticon.com/512/2922/2922561.png"},
            {"name": "Entertainment", "url": "https://cdn-icons-png.flaticon.com/512/733/733585.png"},
            {"name": "Bills", "url": "https://cdn-icons-png.flaticon.com/512/1256/1256650.png"},
            {"name": "Education", "url": "https://cdn-icons-png.flaticon.com/512/3143/3143648.png"},
            {"name": "Groceries", "url": "https://cdn-icons-png.flaticon.com/512/1046/1046857.png"},
            {"name": "Utilities", "url": "https://cdn-icons-png.flaticon.com/512/1087/1087929.png"},
            {"name": "Rent", "url": "https://cdn-icons-png.flaticon.com/512/2933/2933606.png"},
            {"name": "Coffee", "url": "https://cdn-icons-png.flaticon.com/512/3022/3022634.png"},
            {"name": "Gifts", "url": "https://cdn-icons-png.flaticon.com/512/1055/1055672.png"},
            {"name": "Pets", "url": "https://cdn-icons-png.flaticon.com/512/616/616490.png"},
            {"name": "Transport", "url": "https://cdn-icons-png.flaticon.com/512/149/149060.png"},
            {"name": "Insurance", "url": "https://cdn-icons-png.flaticon.com/512/2972/2972185.png"},
            {"name": "Subscriptions", "url": "https://cdn-icons-png.flaticon.com/512/1055/1055687.png"},
            {"name": "Internet", "url": "https://cdn-icons-png.flaticon.com/512/1006/1006771.png"},
            {"name": "Mobile", "url": "https://cdn-icons-png.flaticon.com/512/1087/1087926.png"},
            {"name": "Sports", "url": "https://cdn-icons-png.flaticon.com/512/1040/1040232.png"},
            {"name": "Books", "url": "https://cdn-icons-png.flaticon.com/512/2991/2991156.png"},
            {"name": "Office", "url": "https://cdn-icons-png.flaticon.com/512/3106/3106874.png"},
            {"name": "Car", "url": "https://cdn-icons-png.flaticon.com/512/743/743007.png"},
            {"name": "Taxi", "url": "https://cdn-icons-png.flaticon.com/512/744/744922.png"},
            {"name": "Parking", "url": "https://cdn-icons-png.flaticon.com/512/684/684908.png"},
            {"name": "Maintenance", "url": "https://cdn-icons-png.flaticon.com/512/1995/1995574.png"},
            {"name": "Entertainment 2", "url": "https://cdn-icons-png.flaticon.com/512/3135/3135755.png"},
            {"name": "Charity", "url": "https://cdn-icons-png.flaticon.com/512/2917/2917995.png"},
            {"name": "Loan", "url": "https://cdn-icons-png.flaticon.com/512/2838/2838921.png"},
            {"name": "Savings", "url": "https://cdn-icons-png.flaticon.com/512/263/263142.png"},
            {"name": "Miscellaneous", "url": "https://cdn-icons-png.flaticon.com/512/2917/2917997.png"}
        ]
        return render_template('categories.html', icon_list=icon_list)

@login_required
@app.route('/expenses', methods=['GET', 'POST'])
def create_expenses():
    if request.method == 'POST':
        # Get form values
        total = request.form.get('total')
        date_str = request.form.get('date')
        category_id = request.form.get('category')
        description = request.form.get('description')
        entry_method = request.form.get('entry_method')  # "manual" or "slip"

        # Convert date string to date
        expense_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now().date()

        # Convert total to Decimal
        try:
            amount = Decimal(total)
        except Exception as e:
            amount = Decimal('0.00')

        # Initialize slip_image_url as None
        slip_image_url = None
        if entry_method == 'slip':
            # Handle the file upload if slip is selected
            if 'slip_image' in request.files:
                slip_file = request.files['slip_image']
                if slip_file and slip_file.filename:
                    # Sanitize and build a filename
                    filename = secure_filename(slip_file.filename)
                    # Use an upload folder defined in your config, or set a default folder
                    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    file_path = os.path.join(upload_folder, filename)
                    slip_file.save(file_path)
                    # Store the file path or a URL for later retrieval
                    slip_image_url = file_path

        # Create the expense instance
        new_expense = Expense(
            amount=amount,
            entry_method=entry_method,
            user_id=current_user.id,
            category_id=category_id,
            description=description,
            expense_date=expense_date,
            slip_image_url=slip_image_url
        )

        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('create_expenses'))
    else:
        # For GET, pass in necessary context values
        categories = Category.query.all()
        current_date = datetime.now().strftime('%Y-%m-%d')
        return render_template('expenses.html', categories=categories, current_date=current_date)

@login_required
@app.route('/all_expenses')
def all_expenses():
    
    expenses = Expense.query.all()
    expense_categories = [
        (expense, Category.query.get(expense.category_id))
        for expense in expenses
    ]
    return render_template('all_expenses.html', expense_categories=expense_categories)


@app.route('/upload_icon', methods=['POST'])
def upload_icon():
    if 'file' not in request.files:
        return jsonify(success=False, message="No file part in the request"), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(success=False, message="No selected file"), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Set the upload folder relative to your application's root
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        # Generate a URL that points to the saved file (this will be much shorter than a data URL)
        file_url = url_for('static', filename='uploads/' + filename, _external=True)
        return jsonify(success=True, file_url=file_url)
    else:
        return jsonify(success=False, message="File type not allowed"), 400

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS