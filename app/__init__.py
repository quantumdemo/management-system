from flask import Flask
from config import Config
from .extensions import db, login_manager, mail
from flask_migrate import Migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)
    Migrate(app, db)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.blueprints.students import bp as students_bp
    app.register_blueprint(students_bp, url_prefix='/students')

    from app.blueprints.teachers import bp as teachers_bp
    app.register_blueprint(teachers_bp, url_prefix='/teachers')

    from app.blueprints.classes import bp as classes_bp
    app.register_blueprint(classes_bp, url_prefix='/classes')

    from app.blueprints.attendance import bp as attendance_bp
    app.register_blueprint(attendance_bp, url_prefix='/attendance')

    from app.blueprints.timetable import bp as timetable_bp
    app.register_blueprint(timetable_bp, url_prefix='/timetable')

    from app.blueprints.results import bp as results_bp
    app.register_blueprint(results_bp, url_prefix='/results')

    from app.blueprints.fees import bp as fees_bp
    app.register_blueprint(fees_bp, url_prefix='/fees')

    return app
