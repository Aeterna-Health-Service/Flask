import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """애플리케이션 설정 클래스"""
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 파일 업로드 설정
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # OpenAI 모델 설정
    # 이미지 분석용 모델: gpt-4o, gpt-4-turbo, gpt-4-vision-preview 중 선택
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
    
    @staticmethod
    def init_app(app):
        """애플리케이션 초기화"""
        # 업로드 폴더 생성
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
