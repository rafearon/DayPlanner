import collections, util, copy

import geopy.distance

time_per_mile = 2 # minutes

def find_travel_time(a_latitude, a_longitude, b_latitude, b_longitude):
    coords_1 = (a_latitude, a_longitude)
    coords_2 = (b_latitude, b_longitude)
    distance = geopy.distance.vincenty(coords_1, coords_2).miles
    return distance*time_per_mile


def get_sum_variable(csp, name, variables, maxSum, factor):
    domain = [(a, b) for a in range(0, maxSum + 1) for b in range(0, maxSum + 1)]
    result = ('sum', name, 'aggregated')
    csp.add_variable(result, [a for a in range(0, maxSum + 1)])

    # no input variable, result sum should be 0
    if len(variables) == 0:
        csp.add_unary_factor(result, lambda val: val == 0)
        return result
    
    for i, X_i in enumerate(variables):
        # create auxiliary variable for variable i
        # use systematic naming to avoid naming collision
        A_i = ('sum', name, i)
        csp.add_variable(A_i, domain)

        # incorporate information from X_i
        csp.add_binary_factor(X_i, A_i, factor)

        if i == 0:
            csp.add_unary_factor(A_i, lambda a: a[0] == 0)
        else:
            # consistency between A_{i-1} and A_i
            def factor2(b1, b2):
                return b1[1] == b2[0]
            csp.add_binary_factor(('sum', name, i - 1), A_i, factor2)

            if i == len(variables) - 1:
                csp.add_binary_factor(result, A_i, lambda a, b: a == b[1])
    return result

# A class providing methods to generate CSP that can solve the day scheduling
# problem.
class SchedulingCSPConstructor():

    def __init__(self, activities, restaraunts, profile, genre):
        self.activities = activities[profile.genre]
        self.profile = profile
        self.num_slots = 10 # always keep this even!
        self.restaraunts = restaraunts
        self.max_travel_time = 60 #mins

    def add_variables(self, csp, user_long, user_lat):
        # based on the bay area
        min_latitude = 36.4
        max_latitude = 38.2
        min_longitude = -122.7
        max_longitude = -121.7

        # if we make this delta smaller, it might crash!
        delta = .1

        time_domain = []
        for x in range(0, self.max_travel_time + 1):
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
        home_domain = [{"cost": 0, "duration": 0, "longitude": user_long, "latitude": user_lat, "rating": 5, "is_food": 0}]
        
        # slots (including the travel time)
        for i in range(0, self.num_slots):
            if i == 0:
                csp.add_variable(i, home_domain)
                continue
            if i % 2 == 0:
                csp.add_variable(i, self.activities + self.restaraunts + [None]) # if an activity/restaraunt slot is not assigned, it will be None
            else:
                # travel time
                csp.add_variable(i, time_domain + [None]) # if a time slot is not assigned, it will be duration 0

    # budget: value of (i, "activity") summed up less than user budget
    def add_budget_constraints(self, csp):
        variables = []
        for i in range(0, self.num_slots):
            if i != 0 and i % 2 == 0:
                variables.append(i)
         def factor(a, b):
            val = 0
            if a != None:
                val = a.cost
            return b[1] == b[0] + val
        result = get_sum_variable(csp, "budget", variables, self.profile.budget. factor)
        csp.add_unary_factor(result, lambda val: val <= self.profile.budget)

    # time: value of (i, "activity").duration and (i, "travel").duration summed up less than user time
    def add_time_constraints(self, csp):
        variables = []
        for i in range(0, self.num_slots):
            variables.append(i)
         def factor(a, b):
            val = 0
            if a != None:
                val = a.duration
            return b[1] == b[0] + val
        result = get_sum_variable(csp, "time", variables, self.profile.total_time. factor)
        csp.add_unary_factor(result, lambda val: val <= self.profile.total_time)

    # travel time: unary factor where for each (i, "travel") if less time, then greater weight and vv
    def add_weighted_travel_time_constraints(self, csp):
        for i in range(0, self.num_slots):
            if i % 2 != 0:
                def factor(a):
                    if a == None:
                        return 0.5 # neutral value so we don't promote/demote empty slots
                    else:
                        if a == 0: return .9
                        return 1/a.duration
                csp.add_unary_factor(i, factor)

    # food: sum number of activities that have food, and if they want food it has to equal one or else 0
    def add_food_constraints(self, csp):
        num_restaraunts = self.profile.want_food
        variables = []
        for i in range(0, self.num_slots):
            if i != 0 and i % 2 == 0:
                variables.append(i)
         def factor(a, b):
            val = 0
            if a != None:
                val = a.is_food
            return b[1] == b[0] + val
        result = get_sum_variable(csp, "food", variables, num_restaraunts. factor)
        csp.add_unary_factor(result, lambda val: val == num_restaraunts)

    # travel time: binary factor where for each travel slot, travel_time(prev_activity, next_activity) = travel_time, set (i, "travel") equal to that
    def add_slot_travel_time_constraints(self, csp):
        for i in range(1, self.num_slots):
            if i % 2 != 0:
                def factor_before(a, b):
                    if a is None and b is not None:
                        return 0
                    if a is None and b is None: 
                        return 1
                    if a is not None and b is None:
                        return 1
                    return a.latitude == b.a_latitude and a.longitude == b.a_longitude
                def factor_after(b, a):
                    if b is None and a is not None:
                        return 0
                    if b is None and a is None: 
                        return 1
                    if b is not None and a is None:
                        return 1
                    return a.latitude == b.b_latitude and a.longitude == b.b_longitude
                def factor_duration(a):
                    if a is None:
                        return 1
                    return a.duration == find_travel_time(a.a_latitude, a.a_longitude, b.b_latitude, b.b_longitude)
                csp.add_binary_factor(i-1, i, factor_before)
                csp.add_binary_factor(i, i+1, factor_after)
                csp.add_unary_factor(i, factor_duration)

    # rating: for the value of each (i, "activity"), we give a higher weight for a better rating, UNARY FACTOR
    def add_rating_constraints(self, csp):
        for i in range(1, self.num_slots):
            if i % 2 == 0:
                def factor(a):
                    if a is None:
                        return 1 # in order to promote having filled slots (this is the only place we explicitly promote filled slots)
                    return a.rating
                csp.add_unary_factor(i, factor)
