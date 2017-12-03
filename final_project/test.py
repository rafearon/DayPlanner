min_latitude = 36.4
max_latitude = 38.2
min_longitude = -122.7
max_longitude = -121.7

# if we make this delta smaller, it might crash!
delta = .01
max_travel_time = 60

time_domain = []
for x in range(0, max_travel_time + 1):
    a_latitude = min_latitude
    while a_latitude < max_latitude:
        a_longitude = min_longitude
        while a_longitude < max_longitude:
            b_latitude = min_latitude
            while b_latitude < max_latitude:
                b_longitude = min_longitude
                while b_longitude < max_longitude:
                    time_domain.append({"duration": x, "a_latitude": a_latitude, "a_longitude": a_longitude, "b_latitude": b_latitude, "b_longitude": b_longitude})
                    b_longitude = b_longitude + delta
                b_latitude = b_latitude + delta
            a_longitude = a_longitude + delta
        a_latitude = a_latitude + delta
home_domain = [{"cost": 0, "duration": 0, "longitude": 0.0, "latitude": 0.0, "rating": 5, "is_food": 0}]
