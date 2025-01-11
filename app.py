from flask import Flask, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from flask_mail import Mail
from flask_session import Session
from datetime import datetime, timedelta
import logging
from functools import wraps
from config import Config

mysql = MySQL()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize MySQL and Mail
    mysql.init_app(app)
    mail.init_app(app)
    Session(app)

    @app.route('/check_session', methods=['GET'])
    def check_session():
        # Check if session exists and contains user data
        if "session_id" in session and "user" in session:
            return jsonify({
                "status": "active",
                "session_id": session.get("session_id"),
                "user": session.get("user")
            }), 200
        else:
            return jsonify({
                "status": "inactive",
                "message": "No active session found."
            }), 401
    
    from flask import jsonify, request

    @app.route('/check_cookies', methods=['GET'])
    def check_cookies():
        # Get the session cookies (example: session_id and session_user)
        cookie_session_id = request.cookies.get("session_id")
        cookie_session_user = request.cookies.get("session_user")

        # Check if both cookies exist
        if cookie_session_id and cookie_session_user:
            return jsonify({
                "status": "cookies_found",
                "session_id": cookie_session_id,
                "user": cookie_session_user
            }), 200
        else:
            return jsonify({
                "status": "cookies_not_found",
                "message": "Cookies not found or expired."
            }), 401

    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('static', filename='favicon.ico'))
    
    @app.before_request
    def handle_before_request():
        print(f"Current request endpoint: {request.endpoint}")
        
        # Define public endpoints that don't require session validation
        public_endpoints = [
            'check_session',
            'check_cookies',
            'static',
            'favicon',
            'login.admin_login',
            'login.logout',
            'event.homepage',
            'event.route',
            'event.get_route_image',
            'event.packages',
            'profile.about_us',
            'profile.contact_us',
            'register.public_register',
            'register.student_register',
            'register.submit_form',
            'register.submit_form2',
            'register.payment',
            'register.submit_payment',
        ]

        # Skip session check for public endpoints
        if request.endpoint in public_endpoints:
            return
        
        print(f"Skip request endpoint: {request.endpoint}")
        print(f"Session at app.py: {dict(session)}")

        # Check if the user session exists
        if 'user' not in session:
            flash('Session expired. Please log in again.', 'error')
            session.clear()
            return redirect(url_for('login.admin_login'))

        # Check last activity timestamp
        if 'last_activity' in session:
            session_lifetime = app.permanent_session_lifetime  
            if datetime.now() - session['last_activity'] > session_lifetime:
                print(f"expired!!!!")
                session.clear()
                flash('Session expired. Please log in again.', 'error')
                return redirect(url_for('login.admin_login'))

        # Update last activity timestamp
        session['last_activity'] = datetime.now()

    # Import Blueprints after app initialization to avoid circular imports
    from routes.event_route import event_bp
    app.register_blueprint(event_bp)

    from routes.register_route import register_bp
    app.register_blueprint(register_bp)

    from routes.profile_route import profile_bp
    app.register_blueprint(profile_bp)

    from routes.login_route import login_bp
    app.register_blueprint(login_bp)

    from routes.organiser_route import organiser_bp
    app.register_blueprint(organiser_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return "Page not found.", 404

    # Logging setup
    logging.basicConfig(level=logging.INFO)
    logging.info("App initialized and running.")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)