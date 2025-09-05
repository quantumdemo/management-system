from app.blueprints.students import bp

@bp.route('/')
def index():
    return "This is the students blueprint."
