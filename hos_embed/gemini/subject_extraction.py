from google import genai
import os
import re
api_key = "your gemini api key"
client = genai.Client(api_key)
def extract_subject(text: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=text
        )
        extract_dept = client.models.generate_content(
            model="gemini-2.0-flash", contents=f"예상 진료과를 알려줘.(extract condition : not emotional expression, not using text emphasis expression like bold, italic, just extract department for treatment just plain text+ {response.text}"
        )
        extract_dept = extract_dept.text
        text = re.sub(r'[^\w\s가-힣]','',extract_dept)
        text = re.sub(r'\s+',' ',text)
        print(text)
        return text 
    except Exception as e:
        print(f"Gemini 오류 : {e}")