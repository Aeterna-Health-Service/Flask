from flask import Blueprint, request, jsonify
from services.exercise_service import ExerciseService
from utils.exceptions import FoodAnalysisError
import logging

logger = logging.getLogger(__name__)

exercise_bp = Blueprint('exercise', __name__)

# 지연 초기화를 위한 서비스 인스턴스
_exercise_service = None

def get_exercise_service():
    """ExerciseService 싱글톤 인스턴스 반환"""
    global _exercise_service
    if _exercise_service is None:
        _exercise_service = ExerciseService()
    return _exercise_service


@exercise_bp.route('/calculate-calories', methods=['POST'])
def calculate_exercise_calories():
    """
    운동으로 소모하는 칼로리를 계산하는 API
    
    Request Body:
        - exercise_name: str (운동 이름, 필수)
        - duration_minutes: float (운동 시간(분), 필수)
        - memo: str (메모, 선택사항)
        - weight_kg: float (체중(kg), 선택사항, 없으면 기본값 70kg 사용)
    
    Returns:
        - success: bool
        - exercise_name: str
        - duration_minutes: float
        - memo: str
        - calories_burned: float (소모 칼로리)
        - met_value: float (MET 값)
        - weight_kg: float (사용된 체중)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '요청 데이터가 필요합니다.'
            }), 400
        
        # 필수 필드 검증
        if 'exercise_name' not in data:
            return jsonify({
                'success': False,
                'error': 'exercise_name이 필요합니다.'
            }), 400
        
        if 'duration_minutes' not in data:
            return jsonify({
                'success': False,
                'error': 'duration_minutes가 필요합니다.'
            }), 400
        
        exercise_name = data['exercise_name']
        duration_minutes = data['duration_minutes']
        memo = data.get('memo', '')
        weight_kg = data.get('weight_kg')
        
        # 입력 값 검증
        if not isinstance(exercise_name, str) or not exercise_name.strip():
            return jsonify({
                'success': False,
                'error': 'exercise_name은 비어있을 수 없습니다.'
            }), 400
        
        try:
            duration_minutes = float(duration_minutes)
            if duration_minutes <= 0:
                raise ValueError("duration_minutes는 0보다 커야 합니다.")
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'duration_minutes는 양수여야 합니다.'
            }), 400
        
        if weight_kg is not None:
            try:
                weight_kg = float(weight_kg)
                if weight_kg <= 0:
                    raise ValueError("weight_kg는 0보다 커야 합니다.")
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'weight_kg는 양수여야 합니다.'
                }), 400
        
        # 운동 칼로리 계산
        exercise_service = get_exercise_service()
        result = exercise_service.calculate_calories(
            exercise_name=exercise_name,
            duration_minutes=duration_minutes,
            memo=memo,
            weight_kg=weight_kg
        )
        
        return jsonify({
            'success': True,
            **result
        }), 200
        
    except Exception as e:
        logger.error(f"운동 칼로리 계산 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '서버 오류가 발생했습니다.'
        }), 500


@exercise_bp.route('/exercises', methods=['GET'])
def get_available_exercises():
    """
    사용 가능한 운동 목록을 반환하는 API
    
    Returns:
        - success: bool
        - exercises: list (운동 이름 리스트)
    """
    try:
        exercise_service = get_exercise_service()
        exercises = exercise_service.get_available_exercises()
        
        return jsonify({
            'success': True,
            'exercises': exercises,
            'count': len(exercises)
        }), 200
        
    except Exception as e:
        logger.error(f"운동 목록 조회 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '서버 오류가 발생했습니다.'
        }), 500

