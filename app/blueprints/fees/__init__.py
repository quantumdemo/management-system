from flask import Blueprint

bp = Blueprint('fees', __name__)

from app.blueprints.fees import routes
