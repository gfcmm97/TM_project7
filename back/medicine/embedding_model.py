from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np

# ✅ GPU 있으면 자동으로 사용
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# ✅ 모델 로드 (KoBERT 기반)
model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS", device=device)

def recommend_by_similarity(medicine_list: list, symptom_keywords: list, k: int = 5) -> list:
    """
    KoBERT 임베딩 기반 유사도 계산 + 속도 최적화
    """
    if not medicine_list:
        return []

    # 약물의 효능 문장
    documents = [med.get("efcyQesitm", "") for med in medicine_list]
    query = " ".join(symptom_keywords)

    # ✅ 임베딩 (배치 사이즈 지정)
    doc_embeddings = model.encode(documents, batch_size=32, convert_to_tensor=True, device=device)
    query_embedding = model.encode(query, convert_to_tensor=True, device=device)

    # ✅ Cosine similarity 계산 (빠른 PyTorch 연산)
    cosine_scores = util.cos_sim(query_embedding, doc_embeddings).squeeze().cpu().numpy()

    # ✅ 상위 k개 정렬
    top_k_idx = np.argsort(cosine_scores)[::-1][:k]

    top_k_meds = []
    for idx in top_k_idx:
        med = medicine_list[idx]
        med["similarity"] = round(float(cosine_scores[idx]), 4)
        top_k_meds.append(med)

    return top_k_meds
