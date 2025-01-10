from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from controllers.login_controller import LoginController
from app import mysql

login_bp = Blueprint('login', __name__)

@login_bp.route('/Organiser/login', methods=['GET', 'POST'])
def admin_login():
    controller = LoginController(mysql.connection)
    return controller.login()

@login_bp.route('/Organiser/logout', methods=['GET'])
def logout():
    session["name"] = None
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'success')
    return redirect(url_for('login.admin_login'))

@login_bp.route('/Organiser/update-password', methods=['POST'])
def update_password():
    controller = LoginController(mysql.connection)
    email = request.form['email']  # Assuming the email is passed in the form
    new_password = request.form['password']  # Assuming the new password is passed in the form
    return controller.update_password(email, new_password)
