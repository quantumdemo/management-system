from flask import Blueprint

bp = Blueprint('results', __name__)

from app.blueprints.results import routes
