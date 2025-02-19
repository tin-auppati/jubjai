import json
import secrets
import string
from flask import (jsonify, render_template,
                  request, url_for, flash, redirect)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from sqlalchemy.sql import text

from flask_login import login_user, login_required, logout_user, current_user
from app import app
from app import db
from app import login_manager
from app import oauth
from datetime import datetime

from app.models.contact import Contact
from app.models.jubjai import User,Category,Expense


@app.route('/')
def home():
    return "Flask says 'Hello world!'"

@app.route('/crash')
def crash():
    return 1/0



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
    return render_template('users/profile.html')

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

@app.route('/categories')
def categories():
    all_categories = Category.query.all()
    return render_template('categories.html', categories=all_categories)

@app.route('/expenses')
def expenses():
    all_expenses = Expense.query.all()
    return render_template('expenses.html', expenses=all_expenses)

@app.route('/expense/new', methods=['GET', 'POST'])
def create_expense():
    if request.method == 'POST':
        total = request.form.get('total')
        date_str = request.form.get('date')
        category_id = request.form.get('category')
        description = request.form.get('description')
        # If you have a file input, handle file saving here.

        # Convert date string to date object if provided
        expense_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None

        new_expense = Expense(
            amount=total,
            expense_date=expense_date,
            category_id=category_id,
            description=description,
            # Add other fields (user_id, entry_method, slip_image_url, etc.) as needed
        )
        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('expenses'))  # or wherever you want to go after saving
    else:
        # GET request -> Show the new expense form
        categories = Category.query.all()
        return render_template('new_expense.html', categories=categories)