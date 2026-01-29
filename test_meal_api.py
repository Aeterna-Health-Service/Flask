"""
API 테스트 스크립트
실제 이미지 파일 경로를 사용하여 API를 테스트할 수 있습니다.
"""

import requests
import json
import os

# Flask 서버 URL
BASE_URL = "http://localhost:5000/api/food"

def test_food_name_analysis(image_path: str):
    """음식 이름 분석 API 테스트"""
    print(f"\n=== 음식 이름 분석 테스트 ===")
    print(f"이미지 경로: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
        return
    
    payload = {
        "image_path": image_path
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-name",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"상태 코드: {response.status_code}")
        result = response.json()
        print(f"응답: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('success'):
            print(f"✅ 분석 성공: {result.get('food_name')}")
        else:
            print(f"❌ 분석 실패: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")


def test_food_nutrition_analysis(image_path: str):
    """음식 영양 정보 분석 API 테스트"""
    print(f"\n=== 음식 영양 정보 분석 테스트 ===")
    print(f"이미지 경로: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
        return
    
    payload = {
        "image_path": image_path
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-nutrition",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"상태 코드: {response.status_code}")
        result = response.json()
        print(f"응답: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('success'):
            print(f"✅ 분석 성공:")
            print(f"  - 음식 이름: {result.get('food_name')}")
            print(f"  - 칼로리: {result.get('calories')} kcal")
            nutrition = result.get('nutrition', {})
            print(f"  - 탄수화물: {nutrition.get('carbohydrate')}g")
            print(f"  - 단백질: {nutrition.get('protein')}g")
            print(f"  - 지방: {nutrition.get('fat')}g")
        else:
            print(f"❌ 분석 실패: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")


if __name__ == "__main__":
    # 테스트할 이미지 파일 경로를 여기에 입력하세요
    # 예: test_image_path = "C:/Users/username/Pictures/food.jpg"
    test_image_path = input("테스트할 이미지 파일 경로를 입력하세요: ").strip()
    
    if test_image_path:
        # 음식 이름 분석 테스트
        test_food_name_analysis(test_image_path)
        
        # 영양 정보 분석 테스트
        test_food_nutrition_analysis(test_image_path)
    else:
        print("이미지 경로를 입력해주세요.")
