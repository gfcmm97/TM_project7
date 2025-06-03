# back/services/recommender.py

import os
import numpy as np
import torch
import pandas as pd
import requests
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

# API KEY (개발 중엔 기본값 사용, 배포 시 환경변수 사용)
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBBoNY6prPRJ5LzLLz7BcCzIzPG8HGEMnI")

# 모델 및 데이터 초기화
tokenizer = BertTokenizer.from_pretrained("klue/bert-base")
model = BertModel.from_pretrained("klue/bert-base")
df = pd.read_pickle("../벡터저장/df_all.pkl")
vectors = np.stack(df["벡터"].values)

def gemini_clean_symptom(user_input: str, api_key: str = API_KEY) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    prompt = {
        "contents": [{
            "role": "user",
            "parts": [{"text": f"아래 증상 설명의 오타 없이 깔끔하게 정제해서 한국어로 고쳐줘.\n증상: {user_input}\n→ 정제:"}]
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

def get_bert_embedding(text: str) -> np.ndarray:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def recommend_diseases(user_input: str, top_n: int = 5):
    cleaned = gemini_clean_symptom(user_input)
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
