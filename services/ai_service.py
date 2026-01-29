from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from config import Config
from utils.exceptions import AIServiceError
import base64
import logging
import os

logger = logging.getLogger(__name__)


class AIService:
    """AI 서비스 클래스 - Langchain을 사용한 OpenAI API 연동"""
    
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise AIServiceError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        # 환경 변수에 API 키 설정 (Langchain이 자동으로 읽도록)
        os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
        
        # Langchain ChatOpenAI 초기화
        # 이미지 분석을 위해 gpt-4o 또는 gpt-4-turbo 사용
        # api_key 파라미터를 직접 전달하지 않고 환경 변수 사용
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            max_tokens=1000
        )
    
    def analyze_image(self, image_base64: str, prompt: str) -> str:
        """
        이미지를 분석하여 텍스트 응답 반환
        
        Args:
            image_base64: base64로 인코딩된 이미지
            prompt: 분석 요청 프롬프트
            
        Returns:
            AI 분석 결과 텍스트
        """
        try:
            # 이미지 URL 형식으로 변환
            image_url = f"data:image/jpeg;base64,{image_base64}"
            
            # HumanMessage에 이미지와 텍스트 포함
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            )
            
            # LLM 호출
            response = self.llm.invoke([message])
            
            return response.content
            
        except Exception as e:
            # OpenAI API 호출 실패 시 에러 처리
            error_msg = str(e)
            
            logger.error(f"이미지 분석 API 호출 실패: {error_msg}")
            
            # API 키 관련 에러
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
                raise AIServiceError("OpenAI API 키가 유효하지 않습니다. .env 파일을 확인해주세요.")
            
            # 모델 관련 에러 (gpt-4-vision-preview가 없는 경우)
            if "model" in error_msg.lower() or "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                # 대체 모델로 시도
                alternative_models = ["gpt-4o", "gpt-4-turbo", "gpt-4"]
                for alt_model in alternative_models:
                    try:
                        logger.info(f"대체 모델 시도: {alt_model}")
                        self.llm.model = alt_model
                        response = self.llm.invoke([message])
                        return response.content
                    except Exception as alt_error:
                        logger.warning(f"대체 모델 {alt_model} 실패: {str(alt_error)}")
                        continue
                raise AIServiceError(f"이미지 분석 모델을 사용할 수 없습니다: {error_msg}")
            
            raise AIServiceError(f"이미지 분석 중 오류가 발생했습니다: {error_msg}")
    
    def ask_text(self, prompt: str) -> str:
        """
        텍스트 기반 질의응답
        
        Args:
            prompt: 질문 프롬프트
            
        Returns:
            AI 응답 텍스트
        """
        try:
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            return response.content
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"텍스트 질의 API 호출 실패: {error_msg}")
            
            # API 키 관련 에러
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
                raise AIServiceError("OpenAI API 키가 유효하지 않습니다. .env 파일을 확인해주세요.")
            
            raise AIServiceError(f"텍스트 질의 중 오류가 발생했습니다: {error_msg}")