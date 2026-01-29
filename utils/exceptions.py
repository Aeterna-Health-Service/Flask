"""커스텀 예외 클래스"""


class FoodAnalysisError(Exception):
    """음식 분석 관련 기본 예외"""
    pass


class ImageProcessingError(FoodAnalysisError):
    """이미지 처리 관련 예외"""
    pass


class AIServiceError(FoodAnalysisError):
    """AI 서비스 관련 예외"""
    pass


class InvalidImageError(ImageProcessingError):
    """유효하지 않은 이미지 파일 예외"""
    pass
