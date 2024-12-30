from flask import Blueprint, render_template, request, redirect, url_for, flash
from jinja2 import Environment, FileSystemLoader
from controllers.organiser_controller import OrganiserController
from app import mysql

# Create a Jinja2 environment with the 'enumerate' filter
env = Environment(loader=FileSystemLoader('.'))
env.filters['enumerate'] = enumerate

organiser_bp = Blueprint('organiser', __name__)

@organiser_bp.route('/Organiser/homepage', methods=['GET', 'POST'])
def o_homepage():
    controller = OrganiserController(mysql.connection)
    return controller.handle_homepage(request)

@organiser_bp.route('/Organiser/student_participant_list', methods=['GET'])
def student_participant_list():
    controller = OrganiserController(mysql.connection)
    return controller.student_participant_list()

@organiser_bp.route('/update-status/<matricNumber>', methods=['POST'])
def update_status(matricNumber):
    controller = OrganiserController(mysql.connection)
    return controller.update_status(matricNumber)

@organiser_bp.route('/Organiser/public_participant_list', methods=['GET'])
def public_participant_list():
    controller = OrganiserController(mysql.connection)
    return controller.public_participant_list()

@organiser_bp.route('/update-status2/<ICNumber>', methods=['POST']) 
def update_status2(ICNumber):
    controller = OrganiserController(mysql.connection)
    return controller.update_status2(ICNumber)

@organiser_bp.route('/download_file/<string:user_number>', methods=['GET'])
def download_file(user_number):
    controller = OrganiserController(mysql.connection)
    return controller.download_file(user_number)

@organiser_bp.route('/Organiser/info_list', methods=['GET', 'POST'])
def info_list():
    controller = OrganiserController(mysql.connection)
    if request.method == 'POST':
        controller.handle_route(request)
    event_details = controller.get_route_details()
    return render_template('Organiser/info_list.html', **event_details)

@organiser_bp.route('/Organiser/packages', methods=['GET', 'POST'])
def o_packages():
    controller = OrganiserController(mysql.connection)
    if request.method == 'POST':
        # Process the POST data (handle updates and inserts)
        controller.process_packages_and_items(request.form)
        flash('Your changes have been saved!', 'success')
    else:
        flash('Failed to save changes. Please try again.', 'error')
    
    # Fetch data for display
    return render_template('Organiser/packages.html', **controller.process_packages_and_items(request.form, is_get=True), enumerate=enumerate)

@organiser_bp.route('/Organiser/about_us', methods=['GET', 'POST'])
def about_us():
    controller = OrganiserController(mysql.connection)
    return controller.handle_about_us(request)

@organiser_bp.route('/Organiser/contact_us', methods=['GET', 'POST'])
def contact_us():
    controller = OrganiserController(mysql.connection)
    if request.method == 'POST':
        controller.handle_contact_us(request)
    contact, contact2 = controller.get_contact_us_data()
    return render_template('Organiser/contact_us.html', contact=contact, contact2=contact2)