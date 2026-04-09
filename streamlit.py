import streamlit as st
from PIL import Image
import numpy as np
import json
import os
import re
from ultralytics import YOLO
from fatsecret import Fatsecret
from dotenv import load_dotenv

# 1. 페이지 설정
st.set_page_config(page_title="음식 인식 영양 분석기 (YOLOv8)", layout="centered")
st.title("🍎 어떤 음식인가요? 영양 정보를 알려드려요!")

# 2. YOLO 모델 로드 (캐싱)
@st.cache_resource
def load_yolo_model():
    # 파일명에 주의하세요. 'best.pt' 혹은 'foodfinal.pt' 중 사용하실 파일을 넣으세요.
    model_path = 'best.pt' 
    if not os.path.exists(model_path):
        st.error(f"❌ 모델 파일({model_path})을 찾을 수 없습니다.")
        return None
    model = YOLO(model_path)
    return model

model = load_yolo_model()

# 3. 영양 정보 데이터 로드 (로컬 JSON)
@st.cache_data
def load_nutrition_data():
    try:
        with open('nutrition_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

NUTRITION_DB = load_nutrition_data()
load_dotenv()

# 3-1. FatSecret 세팅 (캐싱 적용으로 인증 안정성 확보)
@st.cache_resource
def get_fs_client(cid, csec):
    # 특수 공백 제거 후 클라이언트 생성
    clean_id = re.sub(r'\s+', '', cid)
    clean_sec = re.sub(r'\s+', '', csec)
    return Fatsecret(clean_id, clean_sec)

# 2. os.getenv를 통해 값을 가져옵니다.
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# 3. 클라이언트 생성
fs = get_fs_client(CLIENT_ID, CLIENT_SECRET)

def get_fatsecret_nutrition(food_name):
    try:
        # 1. 음식 검색
        search_results = fs.foods_search(food_name)
        if not search_results:
            return None
        
        # 2. 첫 번째 결과의 상세 정보 가져오기
        food_id = search_results[0]['food_id']
        food = fs.food_get(food_id)
        
        # 3. 데이터 파싱
        servings = food['servings']['serving']
        # 결과가 여러 개(리스트)인 경우 첫 번째를 사용
        s = servings[0] if isinstance(servings, list) else servings
        
        # 문자열 데이터를 숫자로 변환 (데이터가 없을 경우 0.0)
        return {
            "calories": float(s.get('calories', 0)),
            "carbs": float(s.get('carbohydrate', 0)),
            "protein": float(s.get('protein', 0)),
            "fat": float(s.get('fat', 0)),
            "serving_desc": s.get('serving_description', '1회 제공량')
        }
    except Exception as e:
        st.error(f"⚠️ API 데이터 분석 중 오류: {e}")
        return None

# 4. 사진 업로드 위젯
uploaded_file = st.file_uploader("음식 사진을 업로드하세요...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None and model is not None:
    image = Image.open(uploaded_file)
    st.write("🛠️ YOLOv8 엔진으로 정밀 분석 중...")
    
    # 5. 분석 수행 (신뢰도 임계값 조절 가능)
    results = model.predict(source=image, conf=0.15, verbose=False)
    result = results[0]  
    
    # 결과 시각화
    res_plotted = result.plot()
    res_image = Image.fromarray(res_plotted[:, :, ::-1]) # BGR -> RGB
    st.image(res_image, caption='분석 결과 (탐지된 음식)', use_container_width=True)
    
    # 6. 탐지된 객체 정보 추출 및 합산
    if len(result.boxes) > 0:
        st.success(f"💡 분석 완료! {len(result.boxes)}개의 항목을 찾았습니다.")
        
        # 합산을 위한 데이터 구조
        total_info = {"calories": 0.0, "carbs": 0.0, "protein": 0.0, "fat": 0.0}
        detected_list = []

        # 루프를 돌며 각 음식의 영양 정보 가져오기
        for box in result.boxes:
            class_id = int(box.cls[0])
            label_name = model.names[class_id]
            db_key = label_name.replace(" ", "_").lower()
            
            # --- 영양 정보 가져오기 로직 (info 변수 정의) ---
            current_info = None # 여기서 변수를 초기화하여 NameError 방지
            
            if db_key in NUTRITION_DB:
                current_info = NUTRITION_DB[db_key]
            else:
                # API 호출 (중복 호출을 줄이려면 캐싱이 작동함)
                with st.spinner(f"🌐 '{label_name}' 정보 검색 중..."):
                    current_info = get_fatsecret_nutrition(label_name)
            
            # 정보를 성공적으로 가져온 경우만 리스트에 추가 및 합산
            if current_info:
                total_info["calories"] += current_info.get("calories", 0)
                total_info["carbs"] += current_info.get("carbs", 0)
                total_info["protein"] += current_info.get("protein", 0)
                total_info["fat"] += current_info.get("fat", 0)
                
                detected_list.append({
                    "name": label_name,
                    "cal": current_info.get("calories", 0)
                })

        # 7. 화면에 결과 표시
        st.write("---")
        st.subheader("🍱 오늘의 식단 영양 리포트")

        if detected_list:
            # 메트릭으로 전체 합계 표시
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🔥 총 칼로리", f"{total_info['calories']:.1f} kcal")
            col2.metric("🍞 탄수화물", f"{total_info['carbs']:.1f} g")
            col3.metric("🍗 단백질", f"{total_info['protein']:.1f} g")
            col4.metric("🥓 지방", f"{total_info['fat']:.1f} g")

            # 상세 목록 표시
            with st.expander("🔍 상세 음식 목록 확인"):
                for item in detected_list:
                    st.write(f"- **{item['name']}**: {item['cal']:.1f} kcal")
        else:
            st.warning("⚠️ 탐지된 음식들의 상세 영양 정보를 가져오지 못했습니다.")
            
    else:
        st.warning("⚠️ 사진에서 음식을 탐지하지 못했습니다.")