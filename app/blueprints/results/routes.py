from app.blueprints.results import bp

@bp.route('/')
def index():
    return "This is the results blueprint."
