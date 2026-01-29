"""운동 칼로리 계산 서비스"""

import logging
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ExerciseService:
    """운동 칼로리 계산 서비스 클래스"""
    
    def __init__(self):
        """서비스 초기화"""
        self._ai_service = None
    
    def _get_ai_service(self):
        """AI 서비스 지연 초기화"""
        if self._ai_service is None:
            try:
                from services.ai_service import AIService
                self._ai_service = AIService()
            except Exception as e:
                logger.warning(f"AI 서비스 초기화 실패: {str(e)}")
                self._ai_service = None
        return self._ai_service
    
    # 운동별 MET 값 (Metabolic Equivalent of Task)
    # MET × 체중(kg) × 시간(시간) = 칼로리(kcal)
    EXERCISE_MET_VALUES = {
        # 걷기
        '걷기': 3.5,
        '빠른걷기': 4.5,
        '산책': 3.0,
        '등산': 6.0,
        
        # 달리기
        '달리기': 8.0,
        '조깅': 7.0,
        '마라톤': 13.5,
        '러닝': 8.0,
        
        # 자전거
        '자전거': 6.0,
        '실내자전거': 5.5,
        '로드사이클': 8.0,
        
        # 수영
        '수영': 6.0,
        '자유형': 8.0,
        '평영': 6.0,
        '배영': 6.0,
        '접영': 11.0,
        
        # 근력운동
        '웨이트트레이닝': 5.0,
        '근력운동': 5.0,
        '팔굽혀펴기': 3.5,
        '윗몸일으키기': 3.0,
        '스쿼트': 5.0,
        '플랭크': 3.0,
        
        # 요가/필라테스
        '요가': 3.0,
        '필라테스': 3.0,
        '스트레칭': 2.5,
        
        # 댄스
        '댄스': 5.0,
        '줌바': 7.0,
        '발레': 5.0,
        
        # 구기운동
        '축구': 7.0,
        '농구': 8.0,
        '배구': 4.0,
        '테니스': 7.0,
        '탁구': 4.0,
        '배드민턴': 5.5,
        '골프': 4.5,
        '야구': 5.0,
        
        # 격투기
        '복싱': 12.0,
        '태권도': 8.0,
        '무에타이': 10.0,
        
        # 기타
        '계단오르기': 8.0,
        '줄넘기': 10.0,
        '에어로빅': 6.5,
        '크로스핏': 8.0,
        '헬스': 5.0,
        '조깅머신': 7.0,
        '러닝머신': 8.0,
    }
    
    # 기본 체중 (kg) - 사용자 체중이 없을 경우 사용
    DEFAULT_WEIGHT = 70.0
    
    def calculate_calories(
        self, 
        exercise_name: str, 
        duration_minutes: float,
        memo: Optional[str] = None,
        weight_kg: Optional[float] = None
    ) -> Dict[str, any]:
        """
        운동 칼로리 계산
        
        Args:
            exercise_name: 운동 이름
            duration_minutes: 운동 시간(분)
            memo: 메모 (선택사항)
            weight_kg: 체중(kg) (선택사항, 없으면 기본값 사용)
            
        Returns:
            {
                'exercise_name': str,
                'duration_minutes': float,
                'memo': str,
                'calories_burned': float,
                'met_value': float,
                'weight_kg': float
            }
        """
        # 운동 이름 정규화 (공백 제거, 소문자 변환)
        normalized_name = exercise_name.strip()
        
        # MET 값 찾기 (정확한 매칭 또는 부분 매칭)
        met_value = self._find_met_value(normalized_name)
        
        if met_value is None:
            logger.info(f"알 수 없는 운동: {normalized_name}, AI를 사용하여 MET 값 찾기 시도")
            met_value = self._find_met_value_with_ai(normalized_name)
            
            if met_value is None:
                logger.warning(f"AI로도 MET 값을 찾을 수 없음: {normalized_name}, 기본 MET 값 4.0 사용")
                met_value = 4.0  # 기본값
            else:
                logger.info(f"AI로 MET 값 찾기 성공: {normalized_name} = {met_value}")
        
        # 체중 설정
        weight = weight_kg if weight_kg is not None else self.DEFAULT_WEIGHT
        
        # 시간을 시간 단위로 변환
        duration_hours = duration_minutes / 60.0
        
        # 칼로리 계산: MET × 체중(kg) × 시간(시간)
        calories_burned = met_value * weight * duration_hours
        
        result = {
            'exercise_name': exercise_name,
            'duration_minutes': duration_minutes,
            'memo': memo or '',
            'calories_burned': round(calories_burned, 2),
            'met_value': met_value,
            'weight_kg': weight
        }
        
        logger.info(f"운동 칼로리 계산 완료: {exercise_name}, {duration_minutes}분, {calories_burned:.2f}kcal")
        
        return result
    
    def _find_met_value(self, exercise_name: str) -> Optional[float]:
        """
        운동 이름으로 MET 값 찾기
        
        Args:
            exercise_name: 운동 이름
            
        Returns:
            MET 값 또는 None
        """
        # 정확한 매칭
        if exercise_name in self.EXERCISE_MET_VALUES:
            return self.EXERCISE_MET_VALUES[exercise_name]
        
        # 부분 매칭 (대소문자 무시)
        exercise_name_lower = exercise_name.lower()
        for key, value in self.EXERCISE_MET_VALUES.items():
            if key.lower() in exercise_name_lower or exercise_name_lower in key.lower():
                return value
        
        return None
    
    def _find_met_value_with_ai(self, exercise_name: str) -> Optional[float]:
        """
        AI를 사용하여 운동의 MET 값 찾기
        
        Args:
            exercise_name: 운동 이름
            
        Returns:
            MET 값 또는 None
        """
        ai_service = self._get_ai_service()
        if ai_service is None:
            return None
        
        try:
            prompt = f"""다음 운동의 MET(Metabolic Equivalent of Task) 값을 알려주세요.
MET 값은 운동 강도를 나타내는 수치로, 안정 시 대사율의 배수입니다.

운동 이름: {exercise_name}

다음 형식으로만 답변해주세요:
MET 값: [숫자]

예시:
- 걷기: MET 값: 3.5
- 달리기: MET 값: 8.0
- 수영: MET 값: 6.0

만약 정확한 MET 값을 알 수 없다면, 유사한 운동의 MET 값을 참고하여 추정해주세요.
숫자만 반환해주세요 (예: 5.0)."""

            response = ai_service.ask_text(prompt)
            
            # 응답에서 숫자 추출
            met_match = re.search(r'(\d+\.?\d*)', response)
            if met_match:
                met_value = float(met_match.group(1))
                # MET 값은 보통 1.0 ~ 20.0 사이이므로 유효성 검사
                if 1.0 <= met_value <= 20.0:
                    return met_value
                else:
                    logger.warning(f"AI가 반환한 MET 값이 범위를 벗어남: {met_value}")
                    return None
            else:
                logger.warning(f"AI 응답에서 MET 값을 추출할 수 없음: {response}")
                return None
                
        except Exception as e:
            logger.error(f"AI를 사용한 MET 값 찾기 실패: {str(e)}")
            return None
    
    def get_available_exercises(self) -> list:
        """
        사용 가능한 운동 목록 반환
        
        Returns:
            운동 이름 리스트
        """
        return list(self.EXERCISE_MET_VALUES.keys())

