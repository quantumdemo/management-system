from app.blueprints.timetable import bp

@bp.route('/')
def index():
    return "This is the timetable blueprint."
