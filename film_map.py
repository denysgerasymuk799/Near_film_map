import os
import json
import reverse_geocoder
import pycountry
import folium

from chardet import detect
from pprint import pprint
from location_from_text import find_location_from_name
from third_layer import third_layer


def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']


def create_film_locations_file():
    data_path = os.path.join(os.getcwd(), 'data')
    encode = get_encoding_type(os.path.join(data_path, 'locations2.list'))
    films_json = json.loads('{}')

    with open(os.path.join(data_path, 'locations2.list'), 'r', encoding=encode) as f_locations:
        for line in f_locations.readlines()[14:]:
            line = line.split("(", 1)
            film_title = line[0]
            line = line[1].split(")", 1)
            year = line[0]
            line = line[1].split("}", 1)
            other_data = ''
            try:
                other_data = line[0]
                line = line[1].split("(", 1)

            except:
                pass

            location = line[0]

            if year not in films_json:
                films_json[year] = []
            symbols_remove = '\a\b\f\n\r\t\v'

            film_data = dict()
            film_data['film_title'] = film_title.translate(str.maketrans('', '', symbols_remove)).rstrip().strip()
            film_data['other_data'] = other_data.translate(str.maketrans('', '', symbols_remove)).rstrip().strip()
            film_data['location'] = location.translate(str.maketrans('', '', symbols_remove)).rstrip().strip()

            films_json[year].append(film_data)

    with open(os.path.join(data_path, 'films_data.json'), 'w', encoding=encode) as f_films_data:
        json.dump(films_json, f_films_data, indent=4)

    return films_json


def find_user_location(lat_user, lng_user):
    coordinates = (lat_user, lng_user)
    location = reverse_geocoder.search(coordinates)
    country_cc = location[0]["cc"]
    country = pycountry.countries.get(alpha_2=country_cc)
    name_country = country.name
    name_city = location[0]["name"]
    name_region = location[0]["admin1"]
    if name_country == "United Kingdom":
        name_country = "England"

    elif name_country == "United States":
        name_country = "USA"

    user_text_location = dict()
    user_text_location["name_city"] = name_city
    user_text_location["name_region"] = name_region
    user_text_location["name_country"] = name_country
    return user_text_location


def near_film_data(user_text_location2, year_near):
    all_films_json = create_film_locations_file()
    near_film_titles = []
    near_films_locations = []
    flag_enough = 0
    text_parameters = ["name_city", "name_region", "name_country"]
    n_parameters = [3, 2, 1]
    year_near = str(year_near)
    for n_parameter, text_parameter in zip(n_parameters, text_parameters):
        for place_data_dict in all_films_json[year_near]:
            try:
                length = len(place_data_dict["location"].split(","))
                parameter = place_data_dict["location"].split(",")[length - n_parameter]

                if parameter.endswith("US"):
                    pos_us = parameter.find("US")
                    parameter = parameter[:pos_us] + "USA"

                if (user_text_location2[text_parameter] in parameter) and (place_data_dict["location"] not in near_films_locations):

                    near_films_locations.append(place_data_dict["location"])
                    near_film_titles.append(place_data_dict["film_title"])

                    flag_enough += 1
                    if flag_enough == 100:
                        break

            except:
                pass

        if flag_enough == 100:
            break

    return near_films_locations, near_film_titles


def first_layer(lat_first_layer, lng_first_layer):
    your_loc = folium.FeatureGroup(name="Your location map")
    your_loc.add_child(folium.CircleMarker(location=[lat_first_layer, lng_first_layer], radius=10, popup="You are here",
                                           fill_color='red',
                        color='red', fill_opacity=0.5))
    return your_loc


def second_layer(lat_second_layer, lng_second_layer, year):
    near_stages = folium.FeatureGroup(name="Near stages of films")
    user_text_location2 = find_user_location(lat_second_layer, lng_second_layer)
    near_films_locations, near_film_titles = near_film_data(user_text_location2, year)
    if near_films_locations == []:
        user_text_location2 = find_user_location('42.698334', '23.319941')
        near_films_locations, near_film_titles = near_film_data(user_text_location2, year)

    all_lat_second_layer, all_lng_second_layer = find_location_from_name(near_films_locations)
    for lt, ln, film_title in zip(all_lat_second_layer, all_lng_second_layer, near_film_titles):
        near_stages.add_child(folium.Marker(location=[lt, ln],
                              popup="Film title - " + film_title,
                              icon=folium.Icon()))

    return near_stages


def join_all_layers(lat_first_layer, lng_first_layer, year):
    map = folium.Map(location=[lat_first_layer, lng_first_layer], zoom_start=10)
    your_loc_join = first_layer(lat_first_layer, lng_first_layer)
    near_stages = second_layer(lat_first_layer, lng_first_layer, year)
    unemployment_loc = third_layer(lat_first_layer, lng_first_layer)
    map.add_child(your_loc_join)
    map.add_child(near_stages)
    map.add_child(unemployment_loc)
    map.add_child(folium.LayerControl())
    map.save('2000_movies_map.html')
    print("Finished. Please have look at the map 2000_movies_map.html")


if __name__ == "__main__":
    year = int(input("Please enter a year you would like to have a map for: "))
    lat, lng = input("Please enter your location (format: lat, long): ").split(",")
    lat, lng = float(lat), float(lng)
    print("Map is generating...")
    print("Please wait...")
    if isinstance(year, int) and isinstance(lng, float) and isinstance(lat, float):
        join_all_layers(lat, lng, year)

    else:
        print("Enter right year, lat and lng parameters")