from flask import Blueprint

bp = Blueprint('classes', __name__)

from app.blueprints.classes import routes
