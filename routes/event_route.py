from flask import Blueprint, render_template, redirect, url_for
from controllers.event_controller import EventController
from app import mysql

event_bp = Blueprint('event', __name__)

@event_bp.route('/')
def homepage():
    controller = EventController(mysql.connection)
    data = controller.get_event_details()
    return render_template('Public/homepage.html', events=data['events'], event_date=data['event_date']
                           , sub_details=data['sub_details'], past_images=data['past_images'])

@event_bp.route('/Public/route')
def route():
    controller = EventController(mysql.connection)
    return controller.route()

@event_bp.route('/Public/route/<selected_option>', methods=['GET'])
def get_route_image(selected_option):
    controller = EventController(mysql.connection)
    return controller.get_route_image(selected_option)

@event_bp.route('/Public/packages')
def packages():
    controller = EventController(mysql.connection)
    return controller.packages()