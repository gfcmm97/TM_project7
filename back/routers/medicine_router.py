from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from medicine.recommender import recommend_medicines
from medicine.interaction_filter import filter_conflicting_medicines

router = APIRouter()

class RecommendRequest(BaseModel):
    symptom_keywords: List[str]
    user_medicine: Optional[str] = ""
    top_k: int = 10
    risk_threshold: float = 0.6

@router.post("/recommend/medicine")
def recommend_medicine_endpoint(req: RecommendRequest):
    symptom_keywords = []

    for item in req.symptom_keywords:
        if isinstance(item, str):
            symptom_keywords.extend([kw.strip() for kw in item.split(",")])
        else:
            symptom_keywords.append(item)
        
    results = recommend_medicines(
        symptom_keywords=req.symptom_keywords,
        user_medicine=req.user_medicine,
        top_k=req.top_k,
        risk_threshold=req.risk_threshold
    )
    return results
