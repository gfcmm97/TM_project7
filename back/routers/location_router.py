from fastapi import APIRouter
from services.location import get_location_from_ip

router = APIRouter()

@router.get("/user-location")
def user_location():
    """
    사용자의 IP 기반 위도·경도 및 도시 정보 반환
    """
    return get_location_from_ip()