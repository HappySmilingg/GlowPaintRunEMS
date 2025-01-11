from flask import render_template, request, jsonify, flash, redirect, url_for, session, make_response
from models.login_model import LoginModel
from datetime import datetime 
import bcrypt

class LoginController:
    def __init__(self, db):
        self.db = db
        self.login_model = LoginModel(db)

    def login(self):
        # Check for session in cookies before handling POST requests
        cookie_session_id = request.cookies.get("session_id")
        cookie_session_user = request.cookies.get("session_user")

        if cookie_session_id and cookie_session_user:
            # Match cookies with the current session
            if "session_id" in session and session["session_id"] == cookie_session_id and session["user"] == cookie_session_user:
                print(f"User already logged in via cookies: {cookie_session_user}")
                return redirect(url_for('organiser.o_homepage'))
                
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            user = self.login_model.check_user_credentials(email)

            if user and bcrypt.checkpw(password.encode('utf-8'), user['userPassword'].encode('utf-8')):
                # Set session for the admin
                session["session_id"] = session.sid
                session["user"] = email
                session["last_activity"] = datetime.now()
                session.permanent = True

                resp = make_response(redirect(url_for('organiser.o_homepage')))
                resp.set_cookie("session_id", session["session_id"], httponly=True, secure=False)
                resp.set_cookie("session_user", session["user"], httponly=True, secure=False)
                print(f"Login successful. Session: {dict(session)}")
                flash('Login successful.', 'success')
                return resp
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