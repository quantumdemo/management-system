from flask import Blueprint

bp = Blueprint('timetable', __name__)

from app.blueprints.timetable import routes
