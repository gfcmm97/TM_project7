import os
import urllib.parse
import requests
from dotenv import load_dotenv

# 인증키
load_dotenv()
raw_key = os.getenv("EASYDRUG_API_KEY")
if not raw_key:
    raise RuntimeError("환경변수 EASYDRUG_API_KEY가 설정되지 않았습니다.")
SERVICE_KEY = urllib.parse.quote(raw_key)

# 🔸 약 정보 받아오기 함수
def fetch_medicine_list_by_keywords(keywords: list, max_pages: int = 3):
    """
    Gemini에서 정제된 키워드를 기반으로 효능 정보에 포함된 약을 가져옴
    """
    collected = []
    for page in range(1, max_pages + 1):
        url = (
            f"https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
            f"?serviceKey={SERVICE_KEY}&pageNo={page}&numOfRows=100&type=json"
        )

        res = requests.get(url)
        if res.status_code != 200:
            continue

        try:
            items = res.json().get("body", {}).get("items", [])
        except Exception:
            continue

        # 키워드가 효능(efcyQesitm)에 포함된 약만 필터링
        for item in items:
            efficacy = item.get("efcyQesitm") or ""
            if any(kw in efficacy for kw in keywords):
                collected.append({
                    "itemName": item.get("itemName"),
                    "entpName": item.get("entpName"),
                    "efcyQesitm": efficacy,
                    "itemImage": item.get("itemImage"),
                    "intrcQesitm": item.get("intrcQesitm"),
                    "atpnWarnQesitm": item.get("atpnWarnQesitm"),
                    "seQesitm": item.get("seQesitm"),
                })

    return collected
