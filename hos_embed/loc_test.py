import os
import json
from geopy.geocoders import Nominatim

file_path = "/Users/basamg/KW_2025/tm/project/user_loc.json"
with open(file_path, 'r') as f:
        loc_json = json.load(f)
long = loc_json['longitude']
lati = loc_json['latitude']

coords = f"{lati},{long}"
geolocator = Nominatim(user_agent='basamg')
location = str(geolocator.reverse(coords))
location = location.replace(" ",'')
location = location.replace(",",' ')

