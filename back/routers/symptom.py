from fastapi import APIRouter
from pydantic import BaseModel
from services.recommender import recommend_diseases

router = APIRouter(prefix="/symptom", tags=["Symptom"])

class SymptomInput(BaseModel):
    symptom: str

@router.post("/parse")
def process_symptom(data: SymptomInput):
    cleaned, results = recommend_diseases(data.symptom)
    if not results:
        return {"message": "관련 질병을 찾을 수 없습니다."}
    
    return {
        "정제된_증상": cleaned,
        "관련_질병": results
    }
