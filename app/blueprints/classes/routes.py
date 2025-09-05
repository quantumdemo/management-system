from app.blueprints.classes import bp

@bp.route('/')
def index():
    return "This is the classes blueprint."
