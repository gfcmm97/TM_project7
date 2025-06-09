import requests
import urllib.parse
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
import torch

# 인증키 불러오기
load_dotenv()
raw_key = os.getenv("EASYDRUG_API_KEY")
SERVICE_KEY = urllib.parse.quote(raw_key)

# KoBERT 임베딩 모델 설정
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS", device=device)


def get_risk_text_from_medicine_name(medicine_name: str) -> str:
    """
    상비약 이름으로 위험 설명 텍스트 통합 (상호작용, 경고, 주의사항, 부작용)
    """
    url = (
        f"https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
        f"?serviceKey={SERVICE_KEY}&itemName={urllib.parse.quote(medicine_name)}"
        f"&pageNo=1&numOfRows=1&type=json"
    )
    res = requests.get(url)
    if res.status_code != 200:
        return ""

    try:
        item = res.json().get("body", {}).get("items", [])[0]
    except Exception:
        return ""

    return (
        (item.get("intrcQesitm") or "") + " " +
        (item.get("atpnWarnQesitm") or "") + " " +
        (item.get("atpnQesitm") or "") + " " +
        (item.get("seQesitm") or "")
    )


def filter_conflicting_medicines(medicine_list: list, user_medicine_name: str, threshold: float = 0.5) -> list:
    """
    추천 약 리스트 중 사용자 상비약과 위험하게 상호작용할 가능성이 높은 약 필터링
    """
    user_risk_text = get_risk_text_from_medicine_name(user_medicine_name)
    if not user_risk_text.strip():
        return []

    user_embed = model.encode(user_risk_text, convert_to_tensor=True, device=device)
    risk_list = []

    for med in medicine_list:
        combined_risk_text = (
            (med.get("intrcQesitm") or "") + " " +
            (med.get("atpnWarnQesitm") or "") + " " +
            (med.get("atpnQesitm") or "") + " " +
            (med.get("seQesitm") or "")
        )

        if not combined_risk_text.strip() or len(combined_risk_text.strip()) < 30:
            continue

        med_embed = model.encode(combined_risk_text, convert_to_tensor=True, device=device)
        sim = float(util.cos_sim(user_embed, med_embed).item())
        med["interaction_score"] = round(sim, 4)

        if sim >= threshold:
            print(f"⚠️ 함께 복용 시 위험 약: {med['itemName']} (유사도: {sim:.4f})")
            risk_list.append(med)

    return risk_list
