import os
from config import Config
from PIL import Image


def validate_image_file(file_path: str) -> bool:
    """
    이미지 파일 유효성 검증
    
    Args:
        file_path: 파일 경로
        
    Returns:
        유효한 이미지 파일인지 여부
    """
    try:
        # 파일 확장자 확인
        file_ext = os.path.splitext(file_path)[1][1:].lower()
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            return False
        
        # 파일 크기 확인
        file_size = os.path.getsize(file_path)
        if file_size > Config.MAX_CONTENT_LENGTH:
            return False
        
        # PIL로 이미지 파일 검증
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False
            
    except Exception:
        return False
