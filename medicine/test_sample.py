from recommender import recommend_medicines

keywords = ["발열", "두통"]
user_medicine = "타이레놀"

final_result = recommend_medicines(
    symptom_keywords=keywords,
    user_medicine=user_medicine,
    top_k=10,
    risk_threshold=0.8
)

print("\n✅ 최종 추천 약:")
for med in final_result:
    print(f"[{med['similarity']} / 위험도: {med.get('interaction_score', '-')}] {med['itemName']}")
    print(f"  효능: {med['efcyQesitm']}")
    print(f"  이미지: {med['itemImage']}")
    print("-" * 60)
