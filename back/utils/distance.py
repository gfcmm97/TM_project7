import pandas as pd
from geopy.distance import geodesic
from services.location import get_location_from_ip
from services.kakao_geo import kakao_address_to_latlon

def extract_departments_from_diseases(disease_list: list) -> list:
    departments = set()
    for disease in disease_list:
        raw = disease.get("진료과", "")
        # 괄호 제거 및 쉼표/공백 기준 분리
        cleaned = raw.replace("(", " ").replace(")", " ").replace(",", " ")
        for word in cleaned.split():
            if "과" in word:
                departments.add(word.strip())
    return list(departments)

def filter_hospitals_by_department(df: pd.DataFrame, department: str) -> pd.DataFrame:
    return df[df["medical_subject"].str.contains(department, na=False)]

def compute_distances(department: str, csv_path: str = "../hos_embed/data/hospital_info.csv") -> list:
    user_loc = get_location_from_ip()
    user_coord = (user_loc["latitude"], user_loc["longitude"])
    df = pd.read_csv(csv_path)

    filtered_df = filter_hospitals_by_department(df, department)

    result = []
    for _, row in filtered_df.iterrows():
        address = row["address"]
        hosp_coord = kakao_address_to_latlon(address)
        if hosp_coord:
            distance_km = geodesic(user_coord, hosp_coord).km
            result.append({
                "병원명": row["hospital_name"],
                "주소": address,
                "거리_km": round(distance_km, 2),
                "포함된_진료과": [department]
            })

    return sorted(result, key=lambda x: x["거리_km"])

def compute_distances_multi(dept_list: list[str], csv_path: str = "../hos_embed/data/hospital_info.csv") -> list:
    user_loc = get_location_from_ip()
    user_coord = (user_loc["latitude"], user_loc["longitude"])
    df = pd.read_csv(csv_path)

    filtered_df = df[df["medical_subject"].apply(lambda x: any(dept in str(x) for dept in dept_list))]

    result = []
    for _, row in filtered_df.iterrows():
        address = row["address"]
        hosp_coord = kakao_address_to_latlon(address)
        if hosp_coord:
            distance_km = geodesic(user_coord, hosp_coord).km
            포함과 = [dept for dept in dept_list if dept in str(row["medical_subject"])]
            result.append({
                "병원명": row["hospital_name"],
                "주소": address,
                "거리_km": round(distance_km, 2),
                "포함된_진료과": 포함과
            })

    return sorted(result, key=lambda x: x["거리_km"])
