from geopy.geocoders import Nominatim


def find_location_from_name(near_films_locations_find):
    geolocator = Nominatim(user_agent="specify_your_app_name_here", timeout=3)
    all_latitude = []
    all_longtitude = []
    from geopy.extra.rate_limiter import RateLimiter
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=10, error_wait_seconds=15)
    flag_enough_places = 0
    for point in near_films_locations_find:
        try:
            pos_scene = point.find("(")
            point = point[:pos_scene]
            location = geolocator.geocode(point)
            all_latitude.append(location.latitude)
            all_longtitude.append(location.longitude)
            flag_enough_places += 1
            if flag_enough_places == 10:
                break

        except:
            pass

    return all_latitude, all_longtitude