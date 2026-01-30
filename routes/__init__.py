from flask import Blueprint
from routes.food_analysis import food_analysis_bp
from routes.exercise import exercise_bp
from routes.image_upload import image_upload_bp
from routes.health import health_bp

api_bp = Blueprint('api', __name__)

# 하위 블루프린트 등록
api_bp.register_blueprint(food_analysis_bp, url_prefix='/food')
api_bp.register_blueprint(exercise_bp, url_prefix='/exercise')
api_bp.register_blueprint(image_upload_bp, url_prefix='/image')
api_bp.register_blueprint(health_bp)
