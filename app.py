from flask import Flask
from flask_mysqldb import MySQL
from flask_mail import Mail
from config import Config

mysql = MySQL()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize MySQL and Mail
    mysql.init_app(app)
    mail.init_app(app)

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

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)