import pandas as pd

df = pd.read_csv("data/asan_disease.csv")  # 아산 병원 질병 데이터

def match_disease(symptom: str):
    for _, row in df.iterrows():
        if symptom in row["증상"]:
            return {
                "질병명": row["질병명"],
                "진료과": row["진료과"],
                "설명": row["설명"]
            }
    return None
