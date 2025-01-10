from flask import Blueprint, render_template, redirect, url_for
from controllers.profile_controller import ProfileController
from app import mysql

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/about_us')
def about_us():
    controller = ProfileController(mysql.connection)
    return controller.about_us()

@profile_bp.route('/contact_us')
def contact_us():
    controller = ProfileController(mysql.connection)
    return controller.contact_us()


