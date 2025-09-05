from flask import Blueprint

bp = Blueprint('teachers', __name__)

from app.blueprints.teachers import routes
