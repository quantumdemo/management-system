from app.blueprints.teachers import bp

@bp.route('/')
def index():
    return "This is the teachers blueprint."
