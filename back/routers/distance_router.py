from fastapi import APIRouter, Query
from utils.distance import compute_distances

router = APIRouter()

@router.get("/check-distance")
def check_distance(department: str = Query(..., description="진료과 이름 예: 이비인후과")):
    result = compute_distances(department)
    return {"사용자_기준_병원_거리": result}
