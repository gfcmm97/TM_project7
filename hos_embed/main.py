import os
import pandas as pd
import torch
import json
from gemini.subject_extraction import extract_subject
from model.embeddings import compute_hospital_embed, load_or_create_embed
from model.ranking_hospital import get_query_embedding, extract_hospital_rank_k, show_hospital_k
from model.user_location import get_longi_latitude

ipstack_api_key = "your ipstack api key"

def main():
    ### ipstack 으로부터 유저의 위도 경도를 읻어올 수있다.
    #loc_json = get_longi_latitude(ipstack_api_key)
    # 불러온 json 파일을 저장해둔다. → api 호출 100회/month
    file_path = "user_loc.json"
    #with open(file_path, 'w') as f:
    #    json.dump(loc_json, f)
    with open(file_path, 'r') as f:
        loc_json = json.load(f)
    
    ### code 테스트시
    user_texts = input("증상을 입력해주세요 :")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    hospital_info_path = os.path.join(BASE_DIR, "data", "hospital_info.csv")
    hospital_info = pd.read_csv(hospital_info_path)
    
    embed_path = os.path.join(BASE_DIR,"cache","hospital_embeddings(sroberta-sts-normal,address0.2).pt")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("jhgan/ko-sroberta-sts")
    hospital_embed = load_or_create_embed(hospital_info, model, embed_path)
    
    query_embed = get_query_embedding(user_texts,loc_json)
    candidate_hos = extract_hospital_rank_k(10,hospital_info,query_embed, hospital_embed)
    show_hospital_k(10,candidate_hos)
    
if __name__ == "__main__":
    main()