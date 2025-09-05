from app.blueprints.attendance import bp

@bp.route('/')
def index():
    return "This is the attendance blueprint."
