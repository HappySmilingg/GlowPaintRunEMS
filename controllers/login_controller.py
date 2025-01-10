from flask import render_template, request, jsonify, flash, redirect, url_for, session, current_app
from models.login_model import LoginModel
from datetime import datetime 
import bcrypt

class LoginController:
    def __init__(self, db):
        self.db = db
        self.login_model = LoginModel(db)

    def login(self):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            if "user" in session:
                print(f"userrr: ")
                return redirect(url_for('organiser.o_homepage'))

            user = self.login_model.check_user_credentials(email)

            if user and bcrypt.checkpw(password.encode('utf-8'), user['userPassword'].encode('utf-8')):
                # Set session for the admin
                session["user"] = email
                session["last_activity"] = datetime.now()
                session.permanent = True
                session.modified = True
                print(f"Login successful. Session: {dict(session)}")
                flash('Login successful.', 'success')
                return redirect(url_for('organiser.o_homepage'))
            else:
                flash('Invalid email or password.', 'error')
                return redirect(url_for('login.admin_login'))

        return render_template('Organiser/login.html')

    
    def update_password(self, email, new_password):
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        success = self.login_model.update_user_password(email, hashed_password)
        if success:
            flash('Password updated successfully!', 'success')
        else:
            flash('Failed to update password.', 'error')
        return redirect(url_for('login.admin_login'))