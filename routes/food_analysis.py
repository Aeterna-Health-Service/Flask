from flask import Blueprint, request, jsonify
from services.food_analysis_service import FoodAnalysisService
from utils.exceptions import FoodAnalysisError
import logging

logger = logging.getLogger(__name__)

food_analysis_bp = Blueprint('food_analysis', __name__)

# 지연 초기화를 위한 서비스 인스턴스
_food_service = None

def get_food_service():
    """FoodAnalysisService 싱글톤 인스턴스 반환"""
    global _food_service
    if _food_service is None:
        _food_service = FoodAnalysisService()
    return _food_service


@food_analysis_bp.route('/analyze-name', methods=['POST'])
def analyze_food_name():
    """
    음식 사진을 받아 음식 이름만 반환하는 API
    
    Request Body:
        - image_url: str (이미지 URL)
    
    Returns:
        - food_name: str
    """
    try:
        data = request.get_json()
        
        if not data or 'image_url' not in data:
            return jsonify({
                'success': False,
                'error': 'image_url이 필요합니다.'
            }), 400
        
        image_url = data['image_url']
        
        # 음식 이름 분석
        food_service = get_food_service()
        result = food_service.analyze_food_name(image_url)
        
        return jsonify({
            'success': True,
            'food_name': result
        }), 200
        
    except FoodAnalysisError as e:
        logger.error(f"음식 이름 분석 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"예상치 못한 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '서버 오류가 발생했습니다.'
        }), 500


@food_analysis_bp.route('/analyze-nutrition', methods=['POST'])
def analyze_food_nutrition():
    """
    음식 사진을 받아 음식 이름, 칼로리, 탄단지 비율을 반환하는 API
    
    Request Body:
        - image_url: str (이미지 URL)
    
    Returns:
        - food_name: str
        - calories: float
        - nutrition: dict
            - carbohydrate: float (g)
            - protein: float (g)
            - fat: float (g)
    """
    try:
        data = request.get_json()
        
        if not data or 'image_url' not in data:
            return jsonify({
                'success': False,
                'error': 'image_url이 필요합니다.'
            }), 400
        
        image_url = data['image_url']
        
        # 음식 영양 정보 분석
        food_service = get_food_service()
        result = food_service.analyze_food_nutrition(image_url)
        
        return jsonify({
            'success': True,
            **result
        }), 200
        
    except FoodAnalysisError as e:
        logger.error(f"영양 정보 분석 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"예상치 못한 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '서버 오류가 발생했습니다.'
        }), 500
