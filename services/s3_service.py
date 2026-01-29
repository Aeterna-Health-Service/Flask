import boto3
import os
import logging
from botocore.exceptions import ClientError
from config import Config
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class S3Service:
    """AWS S3 서비스 클래스"""
    
    def __init__(self):
        """S3 서비스 초기화"""
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'ap-northeast-2')
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'aeterna-health-images')
        
        # S3 클라이언트 생성
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region
        )
    
    def upload_file(self, file_path: str, folder: str = 'images') -> str:
        """
        파일을 S3에 업로드
        
        Args:
            file_path: 업로드할 파일의 로컬 경로
            folder: S3 내 저장할 폴더명 (기본값: 'images')
            
        Returns:
            업로드된 파일의 S3 URL
            
        Raises:
            Exception: 업로드 실패 시
        """
        try:
            # 파일명 생성 (타임스탬프 + UUID)
            file_extension = os.path.splitext(file_path)[1]
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
            s3_key = f"{folder}/{unique_filename}"
            
            # 파일 업로드
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': self._get_content_type(file_extension),
                    'ACL': 'public-read'  # 퍼블릭 읽기 허용
                }
            )
            
            # S3 URL 생성
            s3_url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            
            logger.info(f"파일 업로드 성공: {s3_url}")
            return s3_url
            
        except ClientError as e:
            logger.error(f"S3 업로드 실패: {str(e)}")
            raise Exception(f"S3 업로드 실패: {str(e)}")
        except Exception as e:
            logger.error(f"파일 업로드 중 오류 발생: {str(e)}")
            raise
    
    def upload_file_object(self, file_obj, filename: str, folder: str = 'images') -> str:
        """
        파일 객체를 S3에 업로드
        
        Args:
            file_obj: 업로드할 파일 객체
            filename: 원본 파일명
            folder: S3 내 저장할 폴더명 (기본값: 'images')
            
        Returns:
            업로드된 파일의 S3 URL
            
        Raises:
            Exception: 업로드 실패 시
        """
        try:
            # 파일명 생성
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
            s3_key = f"{folder}/{unique_filename}"
            
            # 파일 업로드
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': self._get_content_type(file_extension),
                    'ACL': 'public-read'
                }
            )
            
            # S3 URL 생성
            s3_url = f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            
            logger.info(f"파일 업로드 성공: {s3_url}")
            return s3_url
            
        except ClientError as e:
            logger.error(f"S3 업로드 실패: {str(e)}")
            raise Exception(f"S3 업로드 실패: {str(e)}")
        except Exception as e:
            logger.error(f"파일 업로드 중 오류 발생: {str(e)}")
            raise
    
    def delete_file(self, s3_url: str) -> bool:
        """
        S3에서 파일 삭제
        
        Args:
            s3_url: 삭제할 파일의 S3 URL
            
        Returns:
            삭제 성공 여부
        """
        try:
            # URL에서 키 추출
            # https://bucket-name.s3.region.amazonaws.com/folder/filename.jpg
            s3_key = s3_url.split(f"{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/")[-1]
            
            # 파일 삭제
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"파일 삭제 성공: {s3_url}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 삭제 실패: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"파일 삭제 중 오류 발생: {str(e)}")
            return False
    
    def _get_content_type(self, file_extension: str) -> str:
        """
        파일 확장자에 따른 Content-Type 반환
        
        Args:
            file_extension: 파일 확장자 (.jpg, .png 등)
            
        Returns:
            Content-Type 문자열
        """
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')

