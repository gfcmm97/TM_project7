def refine_symptom(symptom: str) -> str:
    # TODO: Gemini API 연동
    return symptom.replace("많이", "").replace("좀", "").strip()  # 예시 정제
