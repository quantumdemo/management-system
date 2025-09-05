from app.blueprints.fees import bp

@bp.route('/')
def index():
    return "This is the fees blueprint."
