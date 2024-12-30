from flask import render_template, request, jsonify, flash, redirect, url_for
from models.login_model import LoginModel

class LoginController:
    def __init__(self, db):
        self.db = db
        self.login_model = LoginModel(db)

    def login(self):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            # Call model function to check credentials
            user = self.login_model.check_user_credentials(email)

            if user and user['userPassword'] == password:
                return redirect(url_for('organiser.o_homepage'))
            else:
                flash('Invalid email or password.', 'error')
                return redirect(url_for('login.admin_login'))
        
        return render_template('Organiser/login.html')