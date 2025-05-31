gemini 
- subject_extraction.extract_subject(text) : 사용자 입력인 text 에 대한 진료과 추출하는 코드

model
- embeddings.compute_hospital_embed(hospital_info, model) : hospital_info 에 대한 임베딩 진행
- embeddings.load_or_create_embed(hospital_info, model, embed_path) : embed 된 자료 있다면 로드하고 없으면 compute_hospital_embed 로 계산

-ranking_hospital.get_query_embedding(text) : 사용자 입력에 대한 text 를 받아서 임베딩 (768차원)
-ranking_hospital.extract_hospital_rank_k(k, hospital_info, query_embed, hospital_embed) : k개 병원 유사도 순으로 뽑아내기
-ranking.show_hospital_k(k, hospital_rank) : 계산한 hospital_rank 에서 k개 병원에 대한 병원명, 진료과, 주소 확인 (test코드)