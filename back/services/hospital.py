import os
import sys
import json
import torch
import pandas as pd

# hos_embed 폴더 접근 가능하게 만들기
sys.path.append(os.path.abspath("../../hos_embed"))

# hos_embed 내부 모듈 import
from model.ranking_hospital import extract_hospital_rank_k  # type: ignore
from model.user_location import transform_loc  # type: ignore
from sentence_transformers import SentenceTransformer

# 병원 임베딩 모델 로드 (sroberta)
model = SentenceTransformer("jhgan/ko-sroberta-sts")

# 병원 정보, 임베딩 경로 (상황에 맞게 수정 가능)
HOSPITAL_CSV_PATH = "../hos_embed/data/hospital_info.csv"
HOSPITAL_EMBED_PATH = "../hos_embed/cache/hospital_embeddings(sroberta-sts-normal,address0.2).pt"
USER_LOC_JSON_PATH = "../hos_embed/user_loc.json"

# 질의 벡터 생성 함수 (진료과 + 위치 조합)
def get_query_embedding_by_dept_and_loc(department: str, loc_json: dict):
    loc_text = transform_loc(loc_json)
    query_text = f"{department} {loc_text}"
    query_embed = model.encode(query_text, convert_to_tensor=True).cpu()
    return query_embed

# 병원 추천 메인 함수
def recommend_hospitals(department: str, top_k: int = 5):
    # 병원 정보, 임베딩, 위치 로드
    hospital_info = pd.read_csv(HOSPITAL_CSV_PATH)
    hospital_embed = torch.load(HOSPITAL_EMBED_PATH)

    with open(USER_LOC_JSON_PATH, "r", encoding="utf-8") as f:
        loc_json = json.load(f)

    query_embed = get_query_embedding_by_dept_and_loc(department, loc_json)

    hospital_rank = extract_hospital_rank_k(
        top_k,
        hospital_info,
        query_embed,
        hospital_embed
    )

    # 원하는 컬럼만 추려서 dict 리스트로 반환
    result = hospital_rank[["hospital_name", "medical_subject", "address"]].to_dict(orient="records")
    return result
