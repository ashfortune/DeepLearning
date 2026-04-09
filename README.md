# 🍎 음식 인식 영양 분석기 (Food Recognition & Nutritional Analyzer)

YOLOv8 딥러닝 모델을 활용하여 사진 속 음식을 자동으로 인식하고, 해당 음식의 실시간 영양 정보(칼로리, 탄수화물, 단백질, 지방)를 분석해 주는 Streamlit 웹 애플리케이션입니다.

## 🚀 주요 기능
- **정밀 객체 탐지**: YOLOv8 모델을 사용하여 100여 가지 이상의 음식 종류를 실시간으로 탐지합니다.
- **영양 정보 통합 분석**: 탐지된 음식을 바탕으로 FatSecret API를 통해 정확한 영양 데이터를 가져옵니다.
- **다중 탐지 및 합산**: 사진 속 여러 개의 음식을 동시에 찾아내어 전체 식단의 총 영양 성분을 계산합니다.
- **직관적인 UI**: Streamlit을 활용하여 누구나 쉽게 사진을 업로드하고 결과를 확인할 수 있습니다.

## 🛠 기술 스택
- **Language**: Python 3.x
- **Deep Learning**: YOLOv8 (Ultralytics)
- **Web Framework**: Streamlit
- **API**: FatSecret Platform API
- **Data**: Nutrition Data JSON, PIL, NumPy

## 📦 설치 및 실행 방법

### 1. 가상환경 구축 및 라이브러리 설치
```bash
# 가상환경 활성화 (Mac/Linux 기준)
source venv/bin/activate

# 필수 라이브러리 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정
프로젝트 루트에 `.env` 파일을 생성하고 본인의 API 키를 입력합니다.
```env
CLIENT_ID=여러분의_FATSECRET_CLIENT_ID
CLIENT_SECRET=여러분의_FATSECRET_CLIENT_SECRET
```

### 3. 애플리케이션 실행
```bash
streamlit run streamlit.py
```

## 📂 프로젝트 구조
- `streamlit.py`: 메인 웹 애플리케이션 소스 코드
- `best.pt`: 학습된 YOLOv8 모델 가중치 파일
- `nutrition_data.json`: 로컬 영양 성분 데이터베이스
- `requirements.txt`: 설치 필요한 라이브러리 목록
- `.gitignore`: Git 제외 파일 설정

## ⚖️ 라이선스
본 프로젝트는 교육 및 연구 목적으로 제작되었습니다.
