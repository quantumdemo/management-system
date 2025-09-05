from flask import Blueprint

bp = Blueprint('attendance', __name__)

from app.blueprints.attendance import routes
