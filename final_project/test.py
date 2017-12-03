import geopy.distance
from math import radians, cos, sin, asin, sqrt

def find_travel_time(a_latitude, a_longitude, b_latitude, b_longitude):
    coords_1 = (a_latitude, a_longitude)
    coords_2 = (b_latitude, b_longitude)
    distance = geopy.distance.vincenty(coords_1, coords_2).miles
    return distance

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def haversine_miles(lat1, lon1, lat2, lon2):
    return haversine(lat1, lon1, lat2, lon2) * 0.62137119

print find_travel_time(37.423580, -122.170733, 37.332879, -122.087098)
print haversine_miles(37.423580, -122.170733, 37.332879, -122.087098)