# asan_disease_recommender.py

import os
import pandas as pd
import numpy as np
import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import requests

# =======================
# [1] 환경 변수/API KEY
# =======================
# 실제 사용 시, .env 파일이나 환경변수로 관리 추천!
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBBoNY6prPRJ5LzLLz7BcCzIzPG8HGEMnI")

# =======================
# [2] 데이터 로딩 함수
# =======================
def load_data(df_path):
    df = pd.read_pickle(df_path)
    vectors = np.stack(df["벡터"].values)
    return df, vectors

# =======================
# [3] BERT 임베딩 함수
# =======================
def get_bert_embedding(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

# =======================
# [4] Gemini 증상 정제
# =======================
def gemini_clean_symptom(user_input, api_key):
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

# =======================
# [5] Gemini 진료과 예측
# =======================
def predict_department_gemini(disease_name, api_key):
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

# =======================
# [6] 통합 추천 함수
# =======================
def recommend_diseases_and_departments(user_input, df, vectors, top_n, api_key, tokenizer, model):
    cleaned = gemini_clean_symptom(user_input, api_key)
    user_vec = get_bert_embedding(cleaned, tokenizer, model)
    sims = cosine_similarity([user_vec], vectors)[0]
    top_indices = sims.argsort()[::-1]
    seen = set()
    results = []
    for idx in top_indices:
        disease_name = df.iloc[idx]["질병명"]
        sim_score = sims[idx]
        if disease_name not in seen:
            department = predict_department_gemini(disease_name, api_key)
            results.append((disease_name, sim_score, department))
            seen.add(disease_name)
        if len(results) >= top_n:
            break
    return cleaned, results

# =======================
# [7] 메인 실행부
# =======================
if __name__ == "__main__":
    # 모델, 데이터 로딩
    from transformers import BertTokenizer, BertModel
    tokenizer = BertTokenizer.from_pretrained("klue/bert-base")
    model = BertModel.from_pretrained("klue/bert-base")
    df, vectors = load_data("벡터저장/df_all.pkl")

    user_input = input("증상을 입력하세요: ")
    cleaned, results = recommend_diseases_and_departments(user_input, df, vectors, top_n=5, api_key=API_KEY, tokenizer=tokenizer, model=model)

    print(f"\n정제된 증상: {cleaned}")
    print("-" * 80)
    for i, (disease, score, dept) in enumerate(results, 1):
        print(f"{i}. {disease:<25} | 유사도: {score:.4f} | 예상 진료과: {dept}")
    print("-" * 80)
