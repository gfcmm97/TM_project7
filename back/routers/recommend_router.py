from fastapi import APIRouter
from pydantic import BaseModel
from collections import Counter
from services.recommender import (
    gemini_clean_symptom,
    predict_department_gemini,
    calculate_ranked_hospitals,
    generate_keyword_frequency_summary,
    recommend_diseases
)
from utils.distance import compute_distances
from medicine.recommender import recommend_medicines

router = APIRouter()

class SymptomInput(BaseModel):
    symptom: str

@router.post("/recommend/hospitals")
def recommend_hospitals(input: SymptomInput):
    # 1. 증상 정제
    cleaned = gemini_clean_symptom(input.symptom)

    # 2. 질병 추천
    cleaned, disease_results = recommend_diseases(cleaned, top_n=10)
    disease_names = [d["질병명"] for d in disease_results] if disease_results else []

    # 3. 진료과 예측 (질병별)
    departments = [predict_department_gemini(disease) for disease in disease_names]
    departments = [d for d in departments if d != "알 수 없음"]

    if not departments:
        return {
            "정제된_증상": cleaned,
            "추천_질병": [],
            "추천_진료과": [],
            "추천_병원": [],
            "추천_약": [],
            "에러": "진료과를 예측할 수 없습니다. 증상을 다시 입력해주세요."
        }

    # 4. 진료과 Top 3 뽑기
    top_departments = [d for d, _ in Counter(departments).most_common(3)]

    # 5. 병원 추천 (→ 대표 진료과 하나로)
    hospitals = compute_distances(top_departments[0])
    if not hospitals:
        return {
            "정제된_증상": cleaned,
            "추천_질병": disease_names[:3],
            "추천_진료과": top_departments,
            "추천_병원": [],
            "추천_약": [],
            "에러": f"{top_departments[0]}에 해당하는 병원을 찾을 수 없습니다."
        }

    ranked = calculate_ranked_hospitals(hospitals)
    top3_hospitals = []
    for h in ranked[:3]:
        h["키워드_요약"] = generate_keyword_frequency_summary(h.get("keyword_freq", "{}"))
        top3_hospitals.append(h)

    # 질병, 약 추천
    _, disease_results = recommend_diseases(input.symptom)
    disease_names = [d["질병명"] for d in disease_results] if disease_results else []

    medicine_results = recommend_medicines(cleaned, top_k=3, user_medicine="", risk_threshold=0.5)    

    return {
        "정제된_증상": cleaned,
        "추천_질병": disease_names[:3],
        "추천_진료과": top_departments,
        "추천_병원": top3_hospitals,
        "추천_약": medicine_results
    }
