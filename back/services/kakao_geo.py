import os
import requests
from dotenv import load_dotenv

load_dotenv()
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

def kakao_address_to_latlon(address: str):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": address}

    try:
        response = requests.get(url, headers=headers, params=params)
        result = response.json()
        if result["documents"]:
            doc = result["documents"][0]
            return float(doc["y"]), float(doc["x"])  # (latitude, longitude)
    except:
        return None
    return None
