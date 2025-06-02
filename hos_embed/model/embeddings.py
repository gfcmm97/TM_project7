import pandas as pd
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util
import os

model = SentenceTransformer('jhgan/ko-sroberta-sts')

def compute_hospital_embed(hospital_info,model):
    #text_embedding = model.encode(text, convert_to_tensor= True)
    weights = {
        "hospital_name" : 0.1,
        "opening_hours" : 0.1,
        "medical_subject" : 0.4,
        "address" : 0.4
    }
    hospital_embeddings = []
    for i in range( len(hospital_info)) :
        embeddings = []
        for key, weight in weights.items():
            text = str(hospital_info.loc[i,key])
            emb = model.encode([text], convert_to_tensor=True)
            #emb = F.normalize(emb, p=2, dim=1) # 벡터의 크기를 normalize 해서 벡터 길이가 긴 임베딩의 영향을줄인다.
            embeddings.append(emb*weight)
        combined = torch.stack(embeddings).sum(dim=0)
        hospital_embeddings.append(combined)
    return hospital_embeddings

def load_or_create_embed(hospital_info, model, embed_path):
    if not os.path.exists(embed_path):
        hospital_embed = compute_hospital_embed(hospital_info,model)
        torch.save(hospital_embed, embed_path)
        print("hospital_embed 생성")
    else:
        hospital_embed = torch.load(embed_path)
        print("hospital_embed load 완료")
    return hospital_embed
    
# sbert-sts = 11 , 23.07
# sroberta-sts + normalize = 7 , 26
# snunlp not normalized 13 25.63
# 