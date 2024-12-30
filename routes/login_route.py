from flask import Blueprint, render_template, redirect, url_for
from controllers.login_controller import LoginController
from app import mysql

login_bp = Blueprint('login', __name__)

@login_bp.route('/Organiser/login', methods=['GET', 'POST'])
def admin_login():
    controller = LoginController(mysql.connection)
    return controller.login()