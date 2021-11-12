from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user import User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def login_registration_page():
    if 'user_id' in session:
        return redirect('/dashboard')

    return render_template('login_registration.html')

@app.route('/user/register', methods=["POST"])
def register_user():
    all_emails = User.get_all_emails()

    if not User.validate_registration(request.form, all_emails):
        return redirect('/')

    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"],
        "password": pw_hash
    }
    user_id = User.create(data)
    session['user_id'] = user_id

    return redirect('/dashboard')

@app.route('/user/login', methods=['POST'])
def login():
    data = {
        "email": request.form["email"]
    }
    user_in_db = User.get_by_email(data)
    if not user_in_db:
        flash("Invalid Email/Password", "login_error")
        redirect('/')
        return redirect('/')
    if user_in_db and not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Invalid Email/Password", "login_error")
        return redirect('/')
    session['user_id'] = user_in_db.id
    return redirect('/dashboard')

@app.route('/user/logout')
def logout():
    session.clear()
    return redirect('/')