import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from services.location import get_location_from_ip

geolocator = Nominatim(user_agent="my-hospital-distance-checker")

def address_to_latlon(address: str):
    try:
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
    except:
        return None
    return None

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
        hosp_coord = address_to_latlon(address)
        if hosp_coord:
            distance_km = geodesic(user_coord, hosp_coord).km
            result.append({
                "병원명": row["hospital_name"],
                "주소": address,
                "거리_km": round(distance_km, 2)
            })

    return result
