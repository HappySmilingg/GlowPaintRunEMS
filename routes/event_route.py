from flask import Blueprint, render_template, redirect, url_for
from controllers.event_controller import EventController
from app import mysql

event_bp = Blueprint('event', __name__)

@event_bp.route('/')
def homepage():
    controller = EventController(mysql)
    data = controller.homepage_data()
    return render_template('Public/homepage.html', events=data['events'], event_date=data['event_date']
                           , sub_details=data['sub_details'], past_images=data['past_images'])