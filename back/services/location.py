import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
IPSTACK_KEY = os.getenv("IPSTACK_KEY")

def get_location_from_ip() -> dict:
    url = f"https://api.ipstack.com/check?access_key={IPSTACK_KEY}"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("IP 위치 조회 실패")
    data = json.loads(r.text)
    return {
        "ip": data["ip"],
        "city": data["city"],
        "region": data["region_name"],
        "country": data["country_name"],
        "latitude": data["latitude"],
        "longitude": data["longitude"]
    }
