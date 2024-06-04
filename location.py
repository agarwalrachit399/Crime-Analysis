import requests

def get_coordinates(location):
    api_key = 'AIzaSyBeKPHK17GwjpcEXwrLiwToJjpGhUrgcAA'
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
        "key": 'AIzaSyBeKPHK17GwjpcEXwrLiwToJjpGhUrgcAA',
        "components": "country:us",
        "locationrestriction": "circle:100000@34.052235,-118.243683"

    }

    response = requests.get(base_url, params=params)
    results = response.json()

    if "predictions" in results:
        suggestions = [prediction["description"] for prediction in results["predictions"]]
        return suggestions
    else:
        return []
# Example usage

#lat, lng = get_coordinates(location)
# input_text = "1268 West"  # The text the user is typing
# suggestions = get_autocomplete_suggestions(input_text)
# print(suggestions)
