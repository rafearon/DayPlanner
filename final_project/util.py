import json, re
from datetime import datetime
from datetime import timedelta
from enum import Enum


class Time(object):
    duration = 0
    # a_latitude = 0
    # a_longitude = 0
    # b_latitude = 0
    # b_longitude = 0

    def __init__(self, duration, a_latitude, a_longitude, b_latitude, b_longitude):
        self.duration = duration
        # self.a_latitude = a_latitude
        # self.a_longitude = a_longitude
        # self.b_latitude = b_latitude
        # self.b_longitude = b_longitude

    def __str__(self):
        return ('Time{duration: %d, a_latitude: %f, a_longitude: %f, b_latitude: %f, b_longitude: %f}' %
            (self.duration, self.a_latitude, self.a_longitude, self.b_latitude, self.b_longitude))

# General code for representing a weighted CSP (Constraint Satisfaction Problem).
# All variables are being referenced by their index instead of their original
# names.
class CSP:
    def __init__(self):
        # Total number of variables in the CSP.
        self.numVars = 0

        # The list of variable names in the same order as they are added. A
        # variable name can be any hashable objects, for example: int, str,
        # or any tuple with hashtable objects.
        self.variables = []

        # Each key K in this dictionary is a variable name.
        # values[K] is the list of domain values that variable K can take on.
        self.values = {}

        # Each entry is a unary factor table for the corresponding variable.
        # The factor table corresponds to the weight distribution of a variable
        # for all added unary factor functions. If there's no unary function for 
        # a variable K, there will be no entry for K in unaryFactors.
        # E.g. if B \in ['a', 'b'] is a variable, and we added two
        # unary factor functions f1, f2 for B,
        # then unaryFactors[B]['a'] == f1('a') * f2('a')
        self.unaryFactors = {}

        # Each entry is a dictionary keyed by the name of the other variable
        # involved. The value is a binary factor table, where each table
        # stores the factor value for all possible combinations of
        # the domains of the two variables for all added binary factor
        # functions. The table is represented as a dictionary of dictionary.
        #
        # As an example, if we only have two variables
        # A \in ['b', 'c'],  B \in ['a', 'b']
        # and we've added two binary functions f1(A,B) and f2(A,B) to the CSP,
        # then binaryFactors[A][B]['b']['a'] == f1('b','a') * f2('b','a').
        # binaryFactors[A][A] should return a key error since a variable
        # shouldn't have a binary factor table with itself.

        self.binaryFactors = {}

        self.ternaryFactors = {}

    def add_variable(self, var, domain):
        """
        Add a new variable to the CSP.
        """
        if var in self.variables:
            raise Exception("Variable name already exists: %s" % str(var))

        self.numVars += 1
        self.variables.append(var)
        self.values[var] = domain
        self.unaryFactors[var] = None
        self.binaryFactors[var] = dict()
        self.ternaryFactors[var] = dict()

    def get_neighbor_vars(self, var):
        """
        Returns a list of variables which are neighbors of |var|.
        """
        # gets the ternary factor neighbors
        neighbors = set()
        for key in self.ternaryFactors[var].keys():
            neighbors.add(key)
            for key2 in self.ternaryFactors[var][key].keys():
                neighbors.add(key2)
        # print "ternary variables are " , neighbors
        result = neighbors.union(set(self.binaryFactors[var].keys()))
        # print "all resulting variables are " , result
        return list(result)

    def add_ternary_factor(self, var1, var2, var3, factor_func):
        try:
            assert var1 != var2 and var2 != var3 and var1 != var3
        except:
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print '!! Tip:                                                                       !!'
            print '!! You are adding a binary factor over a same variable...                  !!'
            print '!! Please check your code and avoid doing this.                               !!'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            raise

        self.update_ternary_factor_table(var1, var2, var3,
            {val1: {val2: {val3: float(factor_func(val1, val2, val3)) \
                for val3 in self.values[var3]} for val2 in self.values[var2]} for val1 in self.values[var1]})
        self.update_ternary_factor_table(var1, var3, var2,
            {val1: {val3: {val2: float(factor_func(val1, val2, val3)) \
                for val2 in self.values[var2]} for val3 in self.values[var3]} for val1 in self.values[var1]})
        self.update_ternary_factor_table(var2, var1, var3, \
            {val2: {val1: {val3: float(factor_func(val1, val2, val3)) \
                for val3 in self.values[var3]} for val1 in self.values[var1]} for val2 in self.values[var2]})
        self.update_ternary_factor_table(var2, var3, var1, \
            {val2: {val3: {val1: float(factor_func(val1, val2, val3)) \
                for val1 in self.values[var1]} for val3 in self.values[var3]} for val2 in self.values[var2]})
        self.update_ternary_factor_table(var3, var1, var2, \
            {val3: {val1: {val2: float(factor_func(val1, val2, val3)) \
                for val2 in self.values[var2]} for val1 in self.values[var1]} for val3 in self.values[var3]})
        self.update_ternary_factor_table(var3, var2, var1, \
            {val3: {val2: {val1: float(factor_func(val1, val2, val3)) \
                for val1 in self.values[var1]} for val2 in self.values[var2]} for val3 in self.values[var3]})

    def add_unary_factor(self, var, factorFunc):
        """
        Add a unary factor function for a variable. Its factor
        value across the domain will be *merged* with any previously added
        unary factor functions through elementwise multiplication.

        How to get unary factor value given a variable |var| and
        value |val|?
        => csp.unaryFactors[var][val]
        """
        # for everything in the domain, this creates a map from domain value to function output
        factor = {val:float(factorFunc(val)) for val in self.values[var]}
        if self.unaryFactors[var] is not None:
            assert len(self.unaryFactors[var]) == len(factor)
            self.unaryFactors[var] = {val:self.unaryFactors[var][val] * \
                factor[val] for val in factor}
        else:
            self.unaryFactors[var] = factor

    def add_binary_factor(self, var1, var2, factor_func):
        """
        Takes two variable names and a binary factor function
        |factorFunc|, add to binaryFactors. If the two variables already
        had binaryFactors added earlier, they will be *merged* through element
        wise multiplication.

        How to get binary factor value given a variable |var1| with value |val1| 
        and variable |var2| with value |val2|?
        => csp.binaryFactors[var1][var2][val1][val2]
        """
        # never shall a binary factor be added over a single variable
        try:
            assert var1 != var2
        except:
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print '!! Tip:                                                                       !!'
            print '!! You are adding a binary factor over a same variable...                  !!'
            print '!! Please check your code and avoid doing this.                               !!'
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            raise

        self.update_binary_factor_table(var1, var2,
            {val1: {val2: float(factor_func(val1, val2)) \
                for val2 in self.values[var2]} for val1 in self.values[var1]})
        self.update_binary_factor_table(var2, var1, \
            {val2: {val1: float(factor_func(val1, val2)) \
                for val1 in self.values[var1]} for val2 in self.values[var2]})

    def update_binary_factor_table(self, var1, var2, table):
        """
        Private method you can skip for 0c, might be useful for 1c though.
        Update the binary factor table for binaryFactors[var1][var2].
        If it exists, element-wise multiplications will be performed to merge
        them together.
        """
        if var2 not in self.binaryFactors[var1]:
            self.binaryFactors[var1][var2] = table
        else:
            currentTable = self.binaryFactors[var1][var2]
            for i in table:
                for j in table[i]:
                    assert i in currentTable and j in currentTable[i]
                    currentTable[i][j] *= table[i][j]

    def update_ternary_factor_table(self, var1, var2, var3, table):
        """
        Private method you can skip for 0c, might be useful for 1c though.
        Update the binary factor table for binaryFactors[var1][var2].
        If it exists, element-wise multiplications will be performed to merge
        them together.
        """
        if var1 not in self.ternaryFactors or var2 not in self.ternaryFactors[var1] or var3 not in self.ternaryFactors[var1][var2]:
            # print self.ternaryFactors
            self.ternaryFactors[var1][var2] = {var3 : table}
        else:
            currentTable = self.ternaryFactors[var1][var2][var3]
            for i in table:
                for j in table[i]:
                    for k in table[i][j]:
                        assert i in currentTable and j in currentTable[i] and k in currentTable[i][j]
                        currentTable[i][j][k] *= table[i][j][k]

############################################################
# CSP examples.

def create_map_coloring_csp():
    """
    A classic CSP of coloring the map of Australia with 3 colors.
    """
    csp = CSP()
    provinces = ['WA', 'NT', 'Q', 'NSW', 'V', 'SA', 'T']
    neighbors = {
        'SA' : ['WA', 'NT', 'Q', 'NSW', 'V'],
        'NT' : ['WA', 'Q'],
        'NSW' : ['Q', 'V']
    }
    colors = ['red', 'blue', 'green']
    def are_neighbors(a, b):
        return (a in neighbors and b in neighbors[a]) or \
            (b in neighbors and a in neighbors[b])

    # Add the variables and binary factors
    for p in provinces:
        csp.add_variable(p, colors)
    for p1 in provinces:
        for p2 in provinces:
            if are_neighbors(p1, p2):
                # Neighbors cannot have the same color
                csp.add_binary_factor(p1, p2, lambda x, y : x != y)
    return csp

def create_weighted_csp():
    """
    An example demonstrating how to create a weighted CSP.
    """
    csp = CSP()
    csp.add_variable('A', [1, 2, 3])
    csp.add_variable('B', [1, 2, 3, 4, 5])
    csp.add_unary_factor('A', lambda x : x > 1)
    csp.add_unary_factor('A', lambda x : x != 2)
    csp.add_unary_factor('B', lambda y : 1.0 / y)
    csp.add_binary_factor('A', 'B', lambda x, y : x != y)
    return csp

def get_or_variable(csp, name, variables, value):
    """
    Create a new variable with domain [True, False] that can only be assigned to
    True iff at least one of the |variables| is assigned to |value|. You should
    add any necessary intermediate variables, unary factors, and binary
    factors to achieve this. Then, return the name of this variable.

    @param name: Prefix of all the variables that are going to be added.
        Can be any hashable objects. For every variable |var| added in this
        function, it's recommended to use a naming strategy such as
        ('or', |name|, |var|) to avoid conflicts with other variable names.
    @param variables: A list of variables in the CSP that are participating
        in this OR function. Note that if this list is empty, then the returned
        variable created should never be assigned to True.
    @param value: For the returned OR variable being created to be assigned to
        True, at least one of these variables must have this value.

    @return result: The OR variable's name. This variable should have domain
        [True, False] and constraints s.t. it's assigned to True iff at least
        one of the |variables| is assigned to |value|.
    """
    result = ('or', name, 'aggregated')
    csp.add_variable(result, [True, False])

    # no input variable, result should be False
    if len(variables) == 0:
        csp.add_unary_factor(result, lambda val: not val)
        return result

    # Let the input be n variables X0, X1, ..., Xn.
    # After adding auxiliary variables, the factor graph will look like this:
    #
    # ^--A0 --*-- A1 --*-- ... --*-- An --*-- result--^^
    #    |        |                  |
    #    *        *                  *
    #    |        |                  |
    #    X0       X1                 Xn
    #
    # where each "--*--" is a binary constraint and "--^" and "--^^" are unary
    # constraints. The "--^^" constraint will be added by the caller.
    for i, X_i in enumerate(variables):
        # create auxiliary variable for variable i
        # use systematic naming to avoid naming collision
        A_i = ('or', name, i)
        # domain values:
        # - [ prev ]: condition satisfied by some previous X_j
        # - [equals]: condition satisfied by X_i
        # - [  no  ]: condition not satisfied yet
        csp.add_variable(A_i, ['prev', 'equals', 'no'])

        # incorporate information from X_i
        def factor(val, b):
            if (val == value): return b == 'equals'
            return b != 'equals'
        csp.add_binary_factor(X_i, A_i, factor)

        if i == 0:
            # the first auxiliary variable, its value should never
            # be 'prev' because there's no X_j before it
            csp.add_unary_factor(A_i, lambda b: b != 'prev')
        else:
            # consistency between A_{i-1} and A_i
            def factor(b1, b2):
                if b1 in ['equals', 'prev']: return b2 != 'no'
                return b2 != 'prev'
            csp.add_binary_factor(('or', name, i - 1), A_i, factor)

    # consistency between A_n and result
    # hacky: reuse A_i because of python's loose scope
    csp.add_binary_factor(A_i, result, lambda val, res: res == (val != 'no'))
    return result

############################################################
# Day planner specifics.

# Information about an activity:
# self.name: string
# self.unique_id: number
# self.latitude
# self.longitude
# self.rating: int from 1 to 5
# self.duration: in minutes
# self.cost: in dollars (expecting one number)
# self.review_count: number of reviews
# self.is_food: 1 if restaurant else 0
class Activity:
    def __init__(self, unique_id, info, is_restaurant):
        self.name = info['name']
        self.unique_id = unique_id
        self.latitude = float(info['coordinates']['latitude'])
        self.longitude = float(info['coordinates']['longitude'])
        self.rating = float(info['rating'])
        self.duration = int(info['time_spent_minutes'])
        self.cost = Price[info['price'].replace("$", "m")].value if 'price' in info else 0
        self.review_count = int(info['review_count'])
        self.is_food = is_restaurant

    def short_str(self): return self.name

    def __str__(self):
        return ('Activity{name: %s, unique_id: %d, latitude: %f, longitude: %f, rating: %d, duration: %d, cost: %d, review_count: %d is_food: %d}' %
            (self.name, self.unique_id, self.latitude, self.longitude, self.rating, self.duration, self.cost, self.review_count, self.is_food))


# Information about all the activities
class ActivityCollection:
    def __init__(self, profile, pathsByGenre):
        """
        Initialize the collection of activities.

        @param profile: a user profile of preferences
        @param activitiesPath: Path of a file containing all the non-food activities information.
        @param activitiesPath: Path of a file containing all the restaurant information.
        """
        # Read activities
        self.activities = dict((genre, dict()) for genre in pathsByGenre.keys())
        self.cur_id = 0
        for genre, path in pathsByGenre.iteritems():
            self.load_activities(path, genre)
        # add home domain
        home = Activity(-1, {"name": "home", "coordinates": {"longitude": profile.user_longitude, "latitude": profile.user_latitude}, "time_spent_minutes": 0, "rating": 5, "review_count": 0}, False)
        self.activities['home'] = {-1: home}

        # add restaurant dict to user's selected genre
        # self.activities[profile.genre].update(self.activities['food'])

    def load_activities(self, path, genre):
        with open(path, 'r') as activities:
            for a in activities:
                info = json.loads(a)
                if not self.is_valid_activity(info): continue
                activity = Activity(self.cur_id, info, genre == 'food')
                self.activities[genre][activity.unique_id] = activity
                self.cur_id += 1

    def is_valid_activity(self, info):
        return not (info['coordinates']['latitude'] is None or
            info['coordinates']['longitude'] is None)

class Price(Enum):
    # We need to use m instead $ because $ is an illegal character for a var name
    m = 10
    mm = 30
    mmm = 60
    mmmm = 100

# Given the path to a preference file, create Profile instance out of user prefs
class Profile:
    def __init__(self, prefsPath):
        """
        Parses the preference file and generate a student's profile.

        @param prefsPath: Path to a txt file that specifies a student's request
            in a particular format.
        """

        # Read preferences
        self.budget = 100 # max money (in dollars) user will spend
        self.start_time = None # military time HH:MM
        self.end_time = None
        self.total_time = None # minutes
        self.genre = None # indoors, outdoors, thrill
        self.want_food = 0 # 0 or 1
        self.user_latitude = None # default latitude: Stanford Tresidder
        self.user_longitude = None # default longitude: Stanford Tresidder

        for line in open(prefsPath):
            m = re.match('(.*)\\s*#.*', line) # remove comments
            if m: line = m.group(1)
            line = line.strip()
            if len(line) == 0: continue

            # Budget
            m = re.match('budget (.+)', line)
            if m:
                self.budget = int(m.group(1))
                continue

            # Genre
            m = re.match('genre (.+)', line)
            if m:
                genre = m.group(1)
                m = re.match('(indoors|outdoors|thrill)', genre)
                if not m:
                    raise Exception("Invalid genre '%s', want indoors, outdoors, or thrill" % genre)
                self.genre = genre
                continue

            # Want food
            m = re.match('meals (.+)', line)
            if m:
                self.want_food = 1 if m.group(1) == 'yes' else 0
                continue

            # Latitude and longitude coordinates
            m = re.match('latitude (.+)', line)
            if m:
                self.user_latitude = float(m.group(1))
                continue
            m = re.match('longitude (.+)', line)
            if m:
                self.user_longitude = float(m.group(1))
                continue

            # Start and end time
            m = re.match('start_time (.+)', line)
            if m:
                self.start_time = datetime.strptime(m.group(1), '%H:%M')
                continue
            m = re.match('end_time (.+)', line)
            if m:
                self.end_time = datetime.strptime(m.group(1), '%H:%M')
                continue

        # Determine total time
        if not self.start_time or not self.end_time:
            raise Exception("Must specify a valid start and end time")
        self.total_time = (self.end_time - self.start_time).seconds / 60

        if not self.user_latitude or not self.user_longitude:
            raise Exception("Must specify valid starting latitude and longitude coordinates")

        if not self.genre:
            raise Exception("Must specify valid genre")

       # TODO: any other error checking we want to do on user input

    def print_info(self):
        print "Budget: %d" % self.budget
        start_time = self.start_time.strftime('%H:%M')
        end_time = self.end_time.strftime('%H:%M')
        print "Time: %s - %s (total of %d minutes)" % (start_time, end_time, self.total_time)
        print "Genre: %s" % self.genre
        print "Food: %s" % ('yes' if self.want_food else 'no')
        print "Starting coordinates: (%f, %f)" % (self.user_latitude, self.user_longitude)

def print_all_scheduling_solutions_beam(solutions, profile, ac):
    if solutions is None: return
    for s, w in solutions:
        print_scheduling_solution(s, profile, ac)
        print "WEIGHT WAS ", w
        print

def print_all_scheduling_solutions(solutions, profile, ac):
    if solutions is None: return
    for s in solutions:
        print_scheduling_solution(s, profile, ac)
        print

def print_scheduling_solution(solution, profile, ac):
    if solution == None:
        print "No schedule found that satisfied all the constraints."
    # activities = ac[profile.genre].update(ac["food"])
    activities = dict(ac[profile.genre].items() + ac["food"].items())
    # print activities
    time_slots = 11
    # print all activity and time slots first
    for slot in range(time_slots):
        value = solution[slot]
        if value == -1:
            print ac['home'][value]
        elif slot % 2 == 0 and value != None:
            print activities[value]
        else:
            print value

    for key, value in solution.items():
        if not isinstance(key, (int, long)):
            print key, '=', value

def parse_schedule(schedule):
    assignment = {}
    for i, line in enumerate(schedule.splitlines()):
        # Check if line shows an activity
        m = re.match('.*Activity\{.+, unique_id: (.+), latitude.+\}.*', line)
        if m:
            unique_id = int(m.group(1))
            assignment[i] = unique_id
            continue
        # Check if line is aggregate sum variable
        m = re.match('.*\\(\'(sum)\', \'(.+)\', \'(aggregated)\'\) = (.+).*', line)
        if m:
            var = (m.group(1), m.group(2), m.group(3))
            val = int(m.group(4))
            assignment[var] = val
            continue
        # Check if line is aux sum variable
        m = re.match('.*\\(\'(sum)\', \'(.+)\', (.+)\) = \((.+), (.+)\).*', line)
        if m:
            var = (m.group(1), m.group(2), int(m.group(3)))
            val = (int(m.group(4)), int(m.group(5)))
            assignment[var] = val
            continue
        # Check if line is time slot variable
        try:
            val = int(line)
            assignment[i] = val
        except:
            continue

    return assignment

def parse_backtrack_schedule():
    schedule = "\
        The above assignment corresponds to the following itinerary\n\
        Activity{name: home, unique_id: -1, latitude: 37.423580, longitude: -122.170733, rating: 5, duration: 0, cost: 0, review_count: 0 is_food: 0}\n\
        20\n\
        Activity{name: Webb Ranch, unique_id: 101, latitude: 37.405820, longitude: -122.194094, rating: 3, duration: 180, cost: 0, review_count: 63 is_food: 0}\n\
        20\n\
        Activity{name: Cook's Seafood Restaurant & Market, unique_id: 36, latitude: 37.451410, longitude: -122.179660, rating: 4, duration: 30, cost: 30, review_count: 429 is_food: 1}\n\
        30\n\
        Activity{name: Rancho San Antonio Open Space Preserve, unique_id: 194, latitude: 37.332879, longitude: -122.087098, rating: 4, duration: 180, cost: 0, review_count: 597 is_food: 0}\n\
        30\n\
        Activity{name: Back A Yard Caribbean American Grill, unique_id: 85, latitude: 37.472900, longitude: -122.154948, rating: 4, duration: 30, cost: 30, review_count: 1759 is_food: 1}\n\
        20\n\
        Activity{name: home, unique_id: -1, latitude: 37.423580, longitude: -122.170733, rating: 5, duration: 0, cost: 0, review_count: 0 is_food: 0}\n\
        ('sum', 'budget', 3) = (60, 100)\n\
        ('sum', 'budget', 'aggregated') = 100\n\
        ('sum', 'budget', 0) = (0, 10)\n\
        ('sum', 'budget', 2) = (50, 60)\n\
        ('sum', 'budget', 1) = (10, 50)"
    return parse_schedule(schedule)
