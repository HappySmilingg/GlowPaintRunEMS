from flask import Blueprint, render_template
from controllers.register_controller import RegisterController
from app import mysql

register_bp = Blueprint('register', __name__)

@register_bp.route('/Public/public_register')
def public_register():
    register_controller = RegisterController(mysql.connection.cursor())
    return register_controller.public_register()

@register_bp.route('/Public/student_register')
def student_register():
    register_controller = RegisterController(mysql.connection.cursor())
    return register_controller.student_register()

@register_bp.route('/submit-form', methods=['POST'])
def submit_form():
    register_controller = RegisterController(mysql.connection)
    return register_controller.submit_form()

@register_bp.route('/submit-form2', methods=['POST'])
def submit_form2():
    register_controller = RegisterController(mysql.connection)
    return register_controller.submit_form2()

@register_bp.route('/Public/payment', methods=['GET'])
def payment():
    register_controller = RegisterController(mysql.connection.cursor())
    return register_controller.payment()

@register_bp.route('/submit_payment', methods=['POST'])
def submit_payment():
    register_controller = RegisterController(mysql.connection)
    return register_controller.submit_payment()