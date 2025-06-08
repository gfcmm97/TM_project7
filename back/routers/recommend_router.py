from fastapi import APIRouter
from pydantic import BaseModel
from services.recommender import gemini_clean_symptom, predict_department_gemini
from utils.distance import compute_distances

router = APIRouter()

class SymptomInput(BaseModel):
    symptom: str

@router.post("/recommend/hospitals")
def recommend_hospitals(input: SymptomInput):
    cleaned = gemini_clean_symptom(input.symptom)
    department = predict_department_gemini(cleaned)

    if department == "알 수 없음":
        return {
            "정제된_증상": cleaned,
            "추천_진료과": None,
            "근처_병원": [],
            "에러": "진료과를 예측할 수 없습니다. 증상을 다시 입력해주세요."
        }

    hospitals = compute_distances(department)

    if not hospitals:
        return {
            "정제된_증상": cleaned,
            "추천_진료과": department,
            "근처_병원": [],
            "에러": f"{department}에 해당하는 병원을 찾을 수 없습니다."
        }

    return {
        "정제된_증상": cleaned,
        "추천_진료과": department,
        "근처_병원": hospitals
    }
