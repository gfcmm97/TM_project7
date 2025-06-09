from medicine.medicine_api import fetch_medicine_list_by_keywords
from medicine.embedding_model import recommend_by_similarity
from medicine.interaction_filter import filter_conflicting_medicines

def recommend_medicines(symptom_keywords: list, user_medicine: str = "", top_k: int = 10, risk_threshold: float = 0.5) -> list:
    """
    전체 추천 파이프라인 통합 함수
    - symptom_keywords: Gemini 등에서 정제된 사용자 증상 키워드
    - user_medicine: 사용자가 복용 중인 상비약 이름 (없으면 ""로)
    - top_k: 추천 약 개수
    - risk_threshold: 상호작용 유사도 필터링 기준값 (0~1)
    """
    # 1. 증상 기반 약 후보 수집
    candidates = fetch_medicine_list_by_keywords(symptom_keywords)

    if not candidates:
        return []

    # 2. KoBERT 유사도 기반 정렬
    ranked = recommend_by_similarity(candidates, symptom_keywords, k=top_k)
    
    return ranked
