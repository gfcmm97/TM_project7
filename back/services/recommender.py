import os, torch, requests, ast
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

# API KEY
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# 모델 및 데이터 초기화
tokenizer = BertTokenizer.from_pretrained("klue/bert-base")
model = BertModel.from_pretrained("klue/bert-base")
df = pd.read_pickle("../벡터저장/df_all.pkl")
vectors = np.stack(df["벡터"].values)

# 리뷰
REVIEW_CSV_PATH = "../review_score/병원별_키워드_분석.csv"

def gemini_clean_symptom(user_input: str, api_key: str = API_KEY) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    prompt = {
        "contents": [{
            "role": "user",
            "parts": [{
                "text": (
                    f"아래는 환자가 일상 언어로 작성한 증상 설명입니다.\n"
                    f"이 문장을 의사가 이해할 수 있도록 정형화된 의학 용어로 텍스트만 반환해줘.\n"
                    f"가능하면 '상복부 통증', '기침', '인후통'처럼 진료 기록에 사용되는 증상 용어를 써줘.\n"
                    f"마크다운 포맷 (예: *, **, 리스트, 줄바꿈 등)은 사용하지 마.\n"
                    f"단, 사용자의 언어를 이해하기 힘들다면 False를 반환해.\n"
                    f"\n사용자 증상: {user_input}"
                )
            }]
        }]
    }
    response = requests.post(url, json=prompt)
    try:
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception:
        return user_input

def predict_department_gemini(disease_name: str, api_key: str = API_KEY) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    prompt = {
        "contents": [{
            "role": "user",
            "parts": [{
                "text": f"'{disease_name}'이라는 질병을 진료받으려면 어느 진료과(내과, 외과, 이비인후과 등)에 가야 하는지 진료과만 한글로 답해."
            }]
        }]
    }
    response = requests.post(url, json=prompt)
    try:
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip().split('\n')[0]
    except Exception:
        return "알 수 없음"
    
def predict_top_departments(symptom: str, top_k: int = 3):
    cleaned, disease_results = recommend_diseases(symptom, top_n=10)

    if cleaned is None or disease_results is None:
        return cleaned, []

    departments = []
    seen = set()
    for result in disease_results:
        dept = result["진료과"]
        if dept not in seen and dept != "알 수 없음":
            seen.add(dept)
            departments.append(dept)
        if len(departments) >= top_k:
            break

    return cleaned, departments

def get_bert_embedding(text: str) -> np.ndarray:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def recommend_diseases(user_input: str, top_n: int = 5):
    cleaned = gemini_clean_symptom(user_input)

    if cleaned == "False":
        return None, None  # 추천 중단

    user_vec = get_bert_embedding(cleaned)
    sims = cosine_similarity([user_vec], vectors)[0]
    top_indices = sims.argsort()[::-1]
    
    seen = set()
    results = []

    for idx in top_indices:
        disease_name = df.iloc[idx]["질병명"]
        sim_score = sims[idx]
        if disease_name not in seen:
            department = predict_department_gemini(disease_name)
            results.append({
                "질병명": disease_name,
                "유사도": float(sim_score),
                "진료과": department
            })
            seen.add(disease_name)
        if len(results) >= top_n:
            break

    return cleaned, results

def calculate_ranked_hospitals(hospital_list: list):
    """
    리뷰 점수(20점 만점 → 60점 스케일)와 거리 점수(40점 만점)를 결합하여 병원 리스트를 정렬함.
    리뷰: 60%, 거리: 40%
    """
    import os

    # 리뷰 불러오기
    review_df = pd.read_csv(REVIEW_CSV_PATH)
    review_score_map = dict(zip(review_df["hospital"], review_df["score"]))
    review_keyword_map = dict(zip(review_df["hospital"], review_df["keyword_freq"]))

    # 거리 최대값 (정규화를 위한 기준)
    max_distance = max(h["거리_km"] for h in hospital_list) or 1e-5  # 0 나눗셈 방지

    ranked_result = []
    for h in hospital_list:
        name = h["병원명"]
        distance_km = h["거리_km"]

        # 거리 점수 계산: 가까울수록 높음 (0~40점)
        distance_score = (1 - (distance_km / max_distance)) * 40

        # 리뷰 점수 스케일 조정: 원점수 20 → 60점 만점으로 변환
        raw_review_score = review_score_map.get(name, 0)
        review_score = min((raw_review_score / 20) * 60, 60)

        keyword_str = review_keyword_map.get(name, "{}")
        keyword_summary = generate_keyword_frequency_summary(keyword_str)

        h.update({
            "리뷰점수(60점만점)": round(review_score, 2),
            "거리점수(40점만점)": round(distance_score, 2),
            "final_score": round(review_score + distance_score, 2),
            "keyword_freq": keyword_str,
            "키워드_요약": keyword_summary
        })
        ranked_result.append(h)

    # final_score 기준 정렬
    ranked_result.sort(key=lambda x: x["final_score"], reverse=True)
    return ranked_result

def generate_keyword_frequency_summary(keyword_freq_str):
    try:
        freq_dict = ast.literal_eval(keyword_freq_str)
    except Exception:
        return ""

    filtered = [(k, v) for k, v in freq_dict.items() if v > 0]
    if not filtered:
        return ""

    sorted_keywords = sorted(filtered, key=lambda x: x[1], reverse=True)
    phrases = [f"'{k}'({v}회)" for k, v in sorted_keywords]
    return "다음 키워드가 자주 나타났어요:\n" + ", ".join(phrases)