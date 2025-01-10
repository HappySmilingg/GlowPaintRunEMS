from flask import Flask, request, redirect, url_for, session, flash
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

    @app.before_request
    def handle_before_request():
         # Rewrite URL if a matching rule exists
        original_path = request.path
        if original_path.startswith('/static'):
            return
        print(f"Original path: {original_path}")  # Print the original path

        # Apply URL rewriting rules
        rewrite_rules = {
        '/': '/dashboard',  
        '/Public/public_register': '/public_register',
        '/Public/student_register': '/student_register',
        '/Public/payment': '/payment',
        '/Public/route': '/route', 
        '/Public/packages': '/packages',  
        '/Public/contact_us': '/contact_us',
        '/Public/about_us': '/about_us',
        }

        if original_path in rewrite_rules:
            rewritten_path = rewrite_rules[original_path]
            if original_path != rewritten_path:  
                print(f"Rewriting URL: {original_path} -> {rewritten_path}")
                request.environ['PATH_INFO'] = rewritten_path
        print(f"Rewritten path: {request.path}")
        print(f"Current request endpoint: {request.endpoint}")
        
        # Define public endpoints that don't require session validation
        public_endpoints = [
            'static',
            'login.admin_login',
            'login.logout'
            'event.homepage',
            'event.route',
            'event.homepage',
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