from fastapi import APIRouter
from pydantic import BaseModel
from services.recommender import recommend_diseases

router = APIRouter()

class SymptomInput(BaseModel):
    symptom: str

@router.post("/")
def process_symptom(data: SymptomInput):
    cleaned, results = recommend_diseases(data.symptom)
    if not results:
        return {"message": "관련 질병을 찾을 수 없습니다."}
    
    return {
        "정제된_증상": cleaned,
        "추천_질병": results
    }