"""
운동 API 테스트 스크립트
운동 칼로리 계산 API를 테스트할 수 있습니다.
"""

import requests
import json

# Flask 서버 URL
BASE_URL = "http://localhost:5000/api/exercise"


def test_calculate_calories(exercise_name: str, duration_minutes: float, memo: str = "", weight_kg: float = None):
    """운동 칼로리 계산 API 테스트"""
    print(f"\n=== 운동 칼로리 계산 테스트 ===")
    print(f"운동 이름: {exercise_name}")
    print(f"운동 시간: {duration_minutes}분")
    print(f"메모: {memo}")
    if weight_kg:
        print(f"체중: {weight_kg}kg")
    else:
        print(f"체중: 기본값 사용 (70kg)")
    
    payload = {
        "exercise_name": exercise_name,
        "duration_minutes": duration_minutes,
        "memo": memo
    }
    
    if weight_kg:
        payload["weight_kg"] = weight_kg
    
    try:
        response = requests.post(
            f"{BASE_URL}/calculate-calories",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"상태 코드: {response.status_code}")
        result = response.json()
        print(f"응답: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('success'):
            print(f"✅ 계산 성공:")
            print(f"  - 운동 이름: {result.get('exercise_name')}")
            print(f"  - 운동 시간: {result.get('duration_minutes')}분")
            print(f"  - 메모: {result.get('memo')}")
            print(f"  - 소모 칼로리: {result.get('calories_burned')} kcal")
            print(f"  - MET 값: {result.get('met_value')}")
            print(f"  - 사용된 체중: {result.get('weight_kg')}kg")
        else:
            print(f"❌ 계산 실패: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")


def test_get_exercises():
    """사용 가능한 운동 목록 조회 API 테스트"""
    print(f"\n=== 운동 목록 조회 테스트 ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/exercises",
            headers={"Content-Type": "application/json"}
        )
        
        print(f"상태 코드: {response.status_code}")
        result = response.json()
        print(f"응답: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get('success'):
            exercises = result.get('exercises', [])
            count = result.get('count', 0)
            print(f"✅ 조회 성공:")
            print(f"  - 총 운동 개수: {count}개")
            print(f"  - 운동 목록 (처음 10개): {exercises[:10]}")
        else:
            print(f"❌ 조회 실패: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")


def test_error_cases():
    """에러 케이스 테스트"""
    print(f"\n=== 에러 케이스 테스트 ===")
    
    # 1. 필수 필드 누락 테스트
    print("\n1. exercise_name 누락 테스트")
    try:
        response = requests.post(
            f"{BASE_URL}/calculate-calories",
            json={"duration_minutes": 30},
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {result.get('error', 'N/A')}")
    except Exception as e:
        print(f"   ❌ 요청 실패: {str(e)}")
    
    # 2. duration_minutes 누락 테스트
    print("\n2. duration_minutes 누락 테스트")
    try:
        response = requests.post(
            f"{BASE_URL}/calculate-calories",
            json={"exercise_name": "달리기"},
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {result.get('error', 'N/A')}")
    except Exception as e:
        print(f"   ❌ 요청 실패: {str(e)}")
    
    # 3. 잘못된 duration_minutes 값 테스트
    print("\n3. 잘못된 duration_minutes 값 테스트 (음수)")
    try:
        response = requests.post(
            f"{BASE_URL}/calculate-calories",
            json={"exercise_name": "달리기", "duration_minutes": -10},
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답: {result.get('error', 'N/A')}")
    except Exception as e:
        print(f"   ❌ 요청 실패: {str(e)}")
    
    # 4. 알 수 없는 운동 이름 테스트
    print("\n4. 알 수 없는 운동 이름 테스트")
    try:
        response = requests.post(
            f"{BASE_URL}/calculate-calories",
            json={"exercise_name": "알수없는운동", "duration_minutes": 30},
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        print(f"   상태 코드: {response.status_code}")
        if result.get('success'):
            print(f"   ✅ 기본 MET 값으로 계산됨: {result.get('met_value')}")
        else:
            print(f"   응답: {result.get('error', 'N/A')}")
    except Exception as e:
        print(f"   ❌ 요청 실패: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("운동 API 테스트 시작")
    print("=" * 60)
    
    # 1. 운동 목록 조회 테스트
    test_get_exercises()
    
    # 2. 다양한 운동 칼로리 계산 테스트
    print("\n" + "=" * 60)
    print("칼로리 계산 테스트")
    print("=" * 60)
    
    # 기본 테스트 (체중 없이)
    test_calculate_calories("달리기", 30, "아침 운동")
    
    # 체중 포함 테스트
    test_calculate_calories("수영", 45, "수영장 운동", weight_kg=65)
    
    # 다양한 운동 테스트
    test_calculate_calories("걷기", 60, "저녁 산책")
    test_calculate_calories("요가", 60, "요가 클래스", weight_kg=55)
    test_calculate_calories("웨이트트레이닝", 90, "헬스장", weight_kg=75)
    test_calculate_calories("자전거", 40, "자전거 타기")
    test_calculate_calories("랫풀다운", 10, "50kg으로 진행", weight_kg=80)
    
    # 3. 에러 케이스 테스트
    print("\n" + "=" * 60)
    print("에러 케이스 테스트")
    print("=" * 60)
    test_error_cases()
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)

