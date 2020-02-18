import json
import pandas as pd
import requests
import folium


def my_color_function(feature, unemployment_dict):
    """Maps low values to green and high values to red."""
    if unemployment_dict[feature['id']] > 6.5:
        return '#ff0000'
    else:
        return '#008000'


def third_layer(lat_first_layer, lng_first_layer):
    unemployment_loc = folium.FeatureGroup(name="US_Unemployment_Oct2012")
    url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
    us_states = f'{url}/us-states.json'
    US_Unemployment_Oct2012 = f'{url}/US_Unemployment_Oct2012.csv'

    geo_json_data = json.loads(requests.get(us_states).text)
    unemployment = pd.read_csv(US_Unemployment_Oct2012)

    unemployment_dict = unemployment.set_index('State')['Unemployment']

    unemployment_loc.add_child(folium.GeoJson(
        geo_json_data,
        style_function=lambda feature: {
            'fillColor': my_color_function(feature, unemployment_dict),
            'color': 'black',
            'weight': 2,
            'dashArray': '5, 5'
        }
    ))
    return unemployment_loc