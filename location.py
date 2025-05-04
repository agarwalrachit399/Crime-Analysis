import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_coordinates(location):
    api_key = os.getenv('MAPS_API_KEY')
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location,
        "key": api_key,
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        result = response.json()
        if result['results']:
            location_data = result['results'][0]['geometry']['location']
            return location_data['lat'], location_data['lng']
        else:
            return None, None
    else:
        return None, None


def get_autocomplete_suggestions(input_text):
    base_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": input_text,
        "key": os.getenv('MAPS_API_KEY'),
        "components": "country:us",
        "locationrestriction": "circle:100000@34.052235,-118.243683"

    }

    response = requests.get(base_url, params=params)
    results = response.json()
    print("debug",results)

    if "predictions" in results:
        suggestions = [prediction["description"] for prediction in results["predictions"]]
        return suggestions
    else:
        return []



def get_locationiq_data(search_value):


    url = "https://us1.locationiq.com/v1/autocomplete"

    params = {
        "q": search_value,
        "countrycodes": "us",
        "limit": 5,
        "viewbox": "-118.67,33.70,-118.15,34.34",
        "bounded": 1,
        "key": os.getenv('LOCATIONIQ_API_KEY'),

    }
    headers = {"accept": "application/json"}

    response = requests.get(url, params=params, headers=headers)


    results = response.json()  

    location_data = [{result["display_name"]: (result["lat"], result["lon"])} for result in results]
    if len(location_data) > 0:
        return location_data
    else:
        return []
