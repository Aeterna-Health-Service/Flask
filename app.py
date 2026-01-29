from flask import Flask
from flask_cors import CORS
from config import Config
from routes import api_bp
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """Flask 애플리케이션 팩토리 함수"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # CORS 설정 (Spring 서버와 통신을 위해)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 설정 초기화
    Config.init_app(app)
    
    # 블루프린트 등록
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 에러 핸들러 등록
    from utils.exceptions import FoodAnalysisError
    
    @app.errorhandler(FoodAnalysisError)
    def handle_food_analysis_error(e):
        return {'success': False, 'error': str(e)}, 500
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        return {'success': False, 'error': '서버 내부 오류가 발생했습니다.'}, 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
