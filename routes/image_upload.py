from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from services.s3_service import S3Service
from utils.file_validator import validate_image_file
from utils.exceptions import InvalidImageError
from config import Config
import logging

logger = logging.getLogger(__name__)

image_upload_bp = Blueprint('image_upload', __name__)

# 지연 초기화를 위한 서비스 인스턴스
_s3_service = None

def get_s3_service():
    """S3Service 싱글톤 인스턴스 반환"""
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service()
    return _s3_service


@image_upload_bp.route('/upload', methods=['POST'])
def upload_image():
    """
    이미지 파일을 S3에 업로드하는 API
    
    Request:
        - multipart/form-data 형식
        - file: 이미지 파일 (필수)
        - folder: 저장할 폴더명 (선택사항, 기본값: 'images')
    
    Returns:
        - success: bool
        - image_url: str (S3 URL)
        - image_path: str (로컬 임시 경로, 분석용)
    """
    try:
        # 파일 확인
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '파일이 필요합니다.'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '파일이 선택되지 않았습니다.'
            }), 400
        
        # 파일명 검증
        filename = secure_filename(file.filename)
        file_extension = os.path.splitext(filename)[1][1:].lower()
        
        if file_extension not in Config.ALLOWED_EXTENSIONS:
            return jsonify({
                'success': False,
                'error': f'지원하지 않는 파일 형식입니다. 허용된 형식: {", ".join(Config.ALLOWED_EXTENSIONS)}'
            }), 400
        
        # 폴더명 가져오기 (선택사항)
        folder = request.form.get('folder', 'images')
        
        # 임시 파일로 저장 (분석용)
        temp_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(temp_path)
        
        # 파일 검증
        if not validate_image_file(temp_path):
            os.remove(temp_path)
            raise InvalidImageError('유효하지 않은 이미지 파일입니다.')
        
        # S3에 업로드
        s3_service = get_s3_service()
        
        # 파일 객체를 다시 읽어서 업로드
        with open(temp_path, 'rb') as f:
            s3_url = s3_service.upload_file_object(f, filename, folder)
        
        # 임시 파일 삭제 (선택사항 - 분석 후 삭제할 수도 있음)
        # os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'image_url': s3_url,
            'image_path': temp_path  # 분석용 로컬 경로
        }), 200
        
    except InvalidImageError as e:
        logger.error(f"이미지 업로드 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"이미지 업로드 중 예상치 못한 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '이미지 업로드 중 오류가 발생했습니다.'
        }), 500


@image_upload_bp.route('/delete', methods=['POST'])
def delete_image():
    """
    S3에서 이미지 파일을 삭제하는 API
    
    Request Body:
        - image_url: str (삭제할 이미지의 S3 URL)
    
    Returns:
        - success: bool
    """
    try:
        data = request.get_json()
        
        if not data or 'image_url' not in data:
            return jsonify({
                'success': False,
                'error': 'image_url이 필요합니다.'
            }), 400
        
        image_url = data['image_url']
        
        # S3에서 삭제
        s3_service = get_s3_service()
        success = s3_service.delete_file(image_url)
        
        if success:
            return jsonify({
                'success': True,
                'message': '이미지가 삭제되었습니다.'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '이미지 삭제에 실패했습니다.'
            }), 500
        
    except Exception as e:
        logger.error(f"이미지 삭제 중 예상치 못한 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '이미지 삭제 중 오류가 발생했습니다.'
        }), 500

