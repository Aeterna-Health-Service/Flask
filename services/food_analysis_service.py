from services.ai_service import AIService
from utils.exceptions import ImageProcessingError, AIServiceError
import base64
from PIL import Image
import io
import logging
import requests

logger = logging.getLogger(__name__)


class FoodAnalysisService:
    """음식 분석 서비스 클래스"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def analyze_food_name(self, image_url: str) -> str:
        """
        음식 사진에서 음식 이름만 추출
        
        Args:
            image_url: 이미지 URL
            
        Returns:
            음식 이름 (한국어)
            
        Raises:
            ImageProcessingError: 이미지 처리 중 오류 발생
            AIServiceError: AI 서비스 호출 중 오류 발생
        """
        try:
            # 이미지를 base64로 인코딩
            image_base64 = self._encode_image(image_url)
            
            # AI 서비스를 통해 음식 이름 분석
            prompt = """이 이미지에 있는 음식을 분석해주세요. 
                        음식 이름만 한국어로 간단하게 답변해주세요. 
                        예: "김치찌개", "비빔밥", "치킨" 등
                        음식 이름만 출력하고 다른 설명은 하지 마세요."""
            
            food_name = self.ai_service.analyze_image(image_base64, prompt)
            
            logger.info(f"음식 이름 분석 완료: {food_name.strip()}")
            return food_name.strip()
            
        except Exception as e:
            logger.error(f"음식 이름 분석 실패: {str(e)}")
            if isinstance(e, (ImageProcessingError, AIServiceError)):
                raise
            raise AIServiceError(f"음식 이름 분석 중 오류 발생: {str(e)}")
    
    def analyze_food_nutrition(self, image_url: str) -> dict:
        """
        음식 사진에서 음식 이름, 칼로리, 탄단지 비율 추출
        
        Args:
            image_url: 이미지 URL
            
        Returns:
            {
                'food_name': str,
                'calories': float,
                'nutrition': {
                    'carbohydrate': float,
                    'protein': float,
                    'fat': float
                }
            }
            
        Raises:
            ImageProcessingError: 이미지 처리 중 오류 발생
            AIServiceError: AI 서비스 호출 중 오류 발생
        """
        try:
            # 이미지를 base64로 인코딩
            image_base64 = self._encode_image(image_url)
            
            # AI 서비스를 통해 영양 정보 분석
            prompt = """이 이미지에 있는 음식을 분석해주세요.
                        다음 형식의 JSON으로만 답변해주세요:
                        {
                            "food_name": "음식 이름 (한국어)",
                            "calories": 칼로리 (숫자만),
                            "carbohydrate": 탄수화물 그램 수 (숫자만),
                            "protein": 단백질 그램 수 (숫자만),
                            "fat": 지방 그램 수 (숫자만)
                        }

                        예시:
                        {
                            "food_name": "김치찌개",
                            "calories": 250,
                            "carbohydrate": 15.5,
                            "protein": 12.3,
                            "fat": 8.2
                        }

                        JSON 형식만 출력하고 다른 설명은 하지 마세요."""
            
            response = self.ai_service.analyze_image(image_base64, prompt)
            
            # JSON 파싱 및 반환 형식 변환
            import json
            import re
            
            # JSON 부분만 추출 (마크다운 코드 블록 제거)
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response
            
            try:
                nutrition_data = json.loads(json_str)
                
                result = {
                    'food_name': nutrition_data.get('food_name', ''),
                    'calories': float(nutrition_data.get('calories', 0)),
                    'nutrition': {
                        'carbohydrate': float(nutrition_data.get('carbohydrate', 0)),
                        'protein': float(nutrition_data.get('protein', 0)),
                        'fat': float(nutrition_data.get('fat', 0))
                    }
                }
                
                logger.info(f"영양 정보 분석 완료: {result['food_name']}")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 실패: {response[:200]}")
                raise AIServiceError(f"AI 응답을 JSON으로 파싱할 수 없습니다: {response[:200]}")
                
        except Exception as e:
            logger.error(f"영양 정보 분석 실패: {str(e)}")
            if isinstance(e, (ImageProcessingError, AIServiceError)):
                raise
            raise AIServiceError(f"영양 정보 분석 중 오류 발생: {str(e)}")
    
    def _encode_image(self, image_url: str) -> str:
        """
        이미지 URL을 base64로 인코딩
        
        Args:
            image_url: 이미지 URL
            
        Returns:
            base64 인코딩된 이미지 문자열
        """
        try:
            # URL에서 이미지 다운로드
            logger.info(f"이미지 URL에서 다운로드: {image_url}")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            image_data = response.content
            
            # PIL로 이미지 검증 및 최적화
            image = Image.open(io.BytesIO(image_data))
            
            # 이미지 크기 조정 (너무 큰 경우)
            max_size = (1024, 1024)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # JPEG로 변환하여 크기 최적화
            output = io.BytesIO()
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(output, format='JPEG', quality=85)
            image_data = output.getvalue()
            
            # base64 인코딩
            base64_image = base64.b64encode(image_data).decode('utf-8')
            return base64_image
                
        except requests.RequestException as e:
            logger.error(f"이미지 URL 다운로드 실패: {str(e)}")
            raise ImageProcessingError(f"이미지 URL에서 다운로드할 수 없습니다: {str(e)}")
        except Exception as e:
            logger.error(f"이미지 인코딩 실패: {str(e)}")
            raise ImageProcessingError(f"이미지 처리 중 오류가 발생했습니다: {str(e)}")
