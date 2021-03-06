
import collections, util, copy, random
import math
from math import *
import geopy.distance
import collections, util, copy
time_per_mile = 2 # minutes


class ICM():

    def reset_results(self):
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = []

        # List of all optimal solutions found
        self.allOptimalAssignments = []
        self.previousWeight = 0

    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            #if w == 0: print "due to unary factors"
            if w == 0: return w
        for var2, factor in self.csp.binaryFactors[var].iteritems():
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            #if w == 0: print "due to binary factor"
            if w == 0: return w
        for var2 in self.csp.ternaryFactors[var]:
            # print self.csp.ternaryFactors[var], "done", var, "done", var2, "HIIIII"
            for var3, factor in self.csp.ternaryFactors[var][var2].iteritems():
                if var2 not in assignment or var3 not in assignment: continue  # Not assigned yet
                w *= factor[val][assignment[var2]][assignment[var3]]
                #if w == 0: print "due to ternary factor"
                if w == 0: return w
        return w

    def solve(self, csp, max_iterations = 100, initial_assignment = None, gibbs_sampling = False):
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp
        self.gibbs_sampling = gibbs_sampling
       
        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        print "starting ICM"
       
        #assignment = self.get_first_assignment()
        assignment = self.get_assignment_from_backtrack()
        if initial_assignment:
            assignment = initial_assignment
        #assignment = self.get_random_assignment()
        weight = 1
        for _ in range(0, max_iterations):
            assignment, weight = self.icm(assignment, weight)

        self.optimalAssignment = assignment
        print "TOTAL WEIGHT OF ASSIGNMENT =", weight

        print "ending ICM"

    def get_random_assignment(self):
        assignment = {}
        for var in self.csp.variables:
            assignment[var] = random.choice(self.domains[var])
        return assignment

    def get_assignment_from_backtrack(self):
        assignment = {}
        weight = 1
        assignment[0] = -1
        assignment[1] = 20
        assignment[2] = 101
        assignment[3] = 20
        assignment[4] = 36
        assignment[5] = 30
        assignment[6] = 194
        assignment[7] = 30
        assignment[8] = 85
        assignment[9] = 20
        assignment[10] = -1
        assignment[('sum', 'budget', 3)] = (60, 100)
        assignment[('sum', 'budget', 'aggregated')] = 100
        assignment[('sum', 'budget', 0)] = (0, 10)
        assignment[('sum', 'budget', 2)] = (50, 60)
        assignment[('sum', 'budget', 1)] = (10, 50)

        return assignment
        # The above assignment corresponds to the following itinerary
        # Activity{name: home, unique_id: -1, latitude: 37.423580, longitude: -122.170733, rating: 5, duration: 0, cost: 0, review_count: 0 is_food: 0}
        # 20
        # Activity{name: Webb Ranch, unique_id: 101, latitude: 37.405820, longitude: -122.194094, rating: 3, duration: 180, cost: 0, review_count: 63 is_food: 0}
        # 20
        # Activity{name: Cook's Seafood Restaurant & Market, unique_id: 36, latitude: 37.451410, longitude: -122.179660, rating: 4, duration: 30, cost: 30, review_count: 429 is_food: 1}
        # 30
        # Activity{name: Rancho San Antonio Open Space Preserve, unique_id: 194, latitude: 37.332879, longitude: -122.087098, rating: 4, duration: 180, cost: 0, review_count: 597 is_food: 0}
        # 30
        # Activity{name: Back A Yard Caribbean American Grill, unique_id: 85, latitude: 37.472900, longitude: -122.154948, rating: 4, duration: 30, cost: 30, review_count: 1759 is_food: 1}
        # 20
        # Activity{name: home, unique_id: -1, latitude: 37.423580, longitude: -122.170733, rating: 5, duration: 0, cost: 0, review_count: 0 is_food: 0}
        # ('sum', 'budget', 3) = (60, 100)
        # ('sum', 'budget', 'aggregated') = 100
        # ('sum', 'budget', 0) = (0, 10)
        # ('sum', 'budget', 2) = (50, 60)
        # ('sum', 'budget', 1) = (10, 50)

    def get_first_assignment(self):
        assignment = {}
        num_slots = 11

        # assign random assignments to activity slots
        for slot in range(num_slots):
            if slot % 2 == 0:
                assignment[slot] = random.choice(self.domains[slot])

        # assign time slots according to activity slots
        for slot in range(num_slots):
            if slot % 2 != 0:
                for val in self.domains[slot]:
                    delta_weight = self.get_delta_weight(assignment, slot, val)
                    if delta_weight > 0:
                        assignment[slot] = val
                        break

        aux_budget_vars = [
            ('sum', 'budget', 0),
            ('sum', 'budget', 1),
            ('sum', 'budget', 2),
            ('sum', 'budget', 3),
            ('sum', 'budget', 'aggregated'),]
        for var in aux_budget_vars:
            for val in self.domains[var]:
                delta_weight = self.get_delta_weight(assignment, var, val)
                if delta_weight > 0:
                    assignment[var] = val
                    break
        
        for var in self.csp.variables:
            if var not in assignment:
                assignment[var] = random.choice(self.domains[var])

        return assignment

    def icm(self, assignment, weight):

        for var in self.csp.variables:
            #get domain values for current var
            ordered_values = self.domains[var]
            random.shuffle(ordered_values)
            # print "looking at var", var
            # print "possible values", ordered_values

            possible_assignments = [] # list of tuples (assignment, weight)

            #check all possible domain values
            for val in ordered_values:

                #creates a copy of current assignment and makes it None so delta weights can test if adding this variable changes existing weights
                assignCopy = assignment.copy()
                del assignCopy[var]
                deltaWeight = self.get_delta_weight(assignCopy, var, val)

                #checks if new assignment changes weight of graph
                if deltaWeight > 0:
                    assignCopy[var] = val
                    new_weight = weight * deltaWeight
                    possible_assignments.append((assignCopy, new_weight))

            # choose best assignment found, if any
            if len(possible_assignments) != 0:
                assignment, weight = self.get_assignment(possible_assignments)

        return (assignment, weight)

    def get_assignment(self, possible_assignments):
        if not self.gibbs_sampling:
            possible_assignments.sort(key=lambda (assignment, weight): weight, reverse=True)
            return possible_assignments[0]
        else:
            sum_weights = sum(w for a, w in possible_assignments)
            r = random.uniform(0, sum_weights)
            lower_bound = 0
            for a, w in possible_assignments:
                if lower_bound + w >= r:
                    return (a, w)
                lower_bound += w
            assert False, "Shouldn't get here"


class BeamSearch():
    def reset_results(self):
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = {}

        # List of all optimal solutions found
        self.allOptimalAssignments = []

        # List of k partial assignments
        self.kAssignments = []

    def print_stats(self):
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print "Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations)
            print "First assignment took %d operations" % self.firstAssignmentNumOperations
        else:
            print "No solution was found."

    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in self.csp.binaryFactors[var].iteritems():
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        for var2 in self.csp.ternaryFactors[var]:
            # print self.csp.ternaryFactors[var], "done", var, "done", var2, "HIIIII"
            for var3, factor in self.csp.ternaryFactors[var][var2].iteritems():
                if var2 not in assignment or var3 not in assignment: continue  # Not assigned yet
                w *= factor[val][assignment[var2]][assignment[var3]]
                if w == 0: return w
        return w

    def solve(self, csp, mcv = False, ac3 = False, k = 10):
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Set the search heuristics requested asked.
        self.mcv = mcv
        self.ac3 = ac3

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        # Set number of candidate assignments to store at any one time
        self.k = k

        print "starting beamsearch"
        # Perform backtracking search.
        self.beamsearch()
        print "ending beamsearch"
        # Print summary of solutions.
        #self.print_stats()



    def beamsearch(self):
        """
        Perform beam search to find k possible solutions to
        the CSP.
        """

        self.numOperations += 1

        # Init with empty assignments of weight 1
        assignments = [({}, 1)]

        # Number of variables currently assigned
        num_assigned = 0

        for var in self.get_ordered_vars(self.csp):
            extended = self.extend_assignments(assignments, var)
            assignments = self.prune_assignments(extended)
            #print extended
            #print assignments
            num_assigned += 1
            # for a, w in assignments:
            #     print a, w
            if len(assignments) == 0:
                print "no assignments after assigning", var
                break

        self.allAssignments = assignments #[a for a, w in assignments]

    def extend_assignments(self, assignments, var):
        """
        Extends the partial assignments passed in by choosing an unassigned
        variable and returning all possible partial assignments with that
        chosen variable assigned
        """
        ordered_values = self.domains[var]
        extended_assignments = [] # list of tuples of the form (assignment, weight)

        for assignment, weight in assignments:
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    # Copy assignment with new var, val pair into extended assignments
                    #print "dw > 0"
                    newAssignment = copy.deepcopy(assignment)
                    newAssignment[var] = val
                    newWeight = weight * deltaWeight
                    extended_assignments.append((newAssignment, newWeight))

        return extended_assignments

    def prune_assignments(self, assignments):
        """
        Returns the k assignments with the highest weights
        """
        # Sort assignments by weight
        assignments.sort(key=lambda (assignment, weight): weight, reverse=True)

        # Return top k assignments
        #print len(assignments)
        new_assignments = assignments[:self.k]
        return new_assignments


    def get_ordered_vars(self, csp):
        num_slots = 11
        ordered_vars = []
        # food variables
        # ordered_vars.extend([('sum', 'food', 'aggregated'),
        #     ('sum', 'food', 0), ('sum', 'food', 1), ('sum', 'food', 2),
        #     ('sum', 'food', 3), ('sum', 'food', 4)])
        # all slot variables
        ordered_vars.extend(i for i in range(0, num_slots))
        # # activity vars
        # ordered_vars.extend(i for i in range(0, num_slots) if i % 2 == 0)
        # # time vars
        # ordered_vars.extend(i for i in range(0, num_slots) if i % 2 != 0)
        # budget vars
        ordered_vars.extend([
            ('sum', 'budget', 0),
            ('sum', 'budget', 1),
            ('sum', 'budget', 2),
            ('sum', 'budget', 3),
            ('sum', 'budget', 'aggregated')])


        # ordered_vars.extend([
        #     ('sum', 'act_time', 'aggregated'),
        #     ('sum', 'travel_time', 'aggregated'),
        #     ('sum', 'act_time', 4),
        #     ('sum', 'act_time', 3),
        #     ('sum', 'act_time', 2),
        #     ('sum', 'act_time', 1),
        #     ('sum', 'act_time', 0),
        #     ('sum', 'travel_time', 4),
        #     ('sum', 'travel_time', 3),
        #     ('sum', 'travel_time', 2),
        #     ('sum', 'travel_time', 1),
        #     ('sum', 'travel_time', 0)])

        print "assigning variables in beam search in this order:"
        print ordered_vars

        assert(len(self.csp.variables) == len(ordered_vars))
        return ordered_vars

# A backtracking algorithm that solves weighted CSP.
# Usage:
#   search = BacktrackingSearch()
#   search.solve(csp)
class BacktrackingSearch():

    def reset_results(self):
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = []

        # List of all optimal solutions found
        self.allOptimalAssignments = []

    def print_stats(self):
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print "Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations)
            print "First assignment took %d operations" % self.firstAssignmentNumOperations
        else:
            print "No solution was found."

    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in self.csp.binaryFactors[var].iteritems():
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        for var2 in self.csp.ternaryFactors[var]:
            # print self.csp.ternaryFactors[var], "done", var, "done", var2, "HIIIII"
            for var3, factor in self.csp.ternaryFactors[var][var2].iteritems():
                if var2 not in assignment or var3 not in assignment: continue  # Not assigned yet
                w *= factor[val][assignment[var2]][assignment[var3]]
                if w == 0: return w
        return w

    def solve(self, csp, mcv = False, ac3 = False, max_num_assignments = 10):
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Set the search heuristics requested asked.
        self.mcv = mcv
        self.ac3 = ac3

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        # Set maximum number of assignments
        self.max_num_assignments = max_num_assignments

        print "starting backtrack"
        # Perform backtracking search.
        self.backtrack({}, 0, 1)
        print "ending backtrack"
        # Print summary of solutions.
        self.print_stats()

    def backtrack(self, assignment, numAssigned, weight):
        """
        Perform the back-tracking algorithms to find all possible solutions to
        the CSP.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param numAssigned: Number of currently assigned variables
        @param weight: The weight of the current partial assignment.
        """

        self.numOperations += 1
        assert weight > 0

        if self.numAssignments >= self.max_num_assignments: return

        if numAssigned == self.csp.numVars:
            # A satisfiable solution have been found. Update the statistics.
            self.numAssignments += 1
            newAssignment = {}
            for var in self.csp.variables:
                newAssignment[var] = assignment[var]
            self.allAssignments.append(newAssignment)

            if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:
                if weight == self.optimalWeight:
                    self.numOptimalAssignments += 1
                    self.allOptimalAssignments.append(newAssignment)
                else:
                    self.numOptimalAssignments = 1
                    self.allOptimalAssignments = [newAssignment]
                self.optimalWeight = weight

                self.optimalAssignment = newAssignment
                if self.firstAssignmentNumOperations == 0:
                    self.firstAssignmentNumOperations = self.numOperations
            return

        # Select the next variable to be assigned.
        var = self.get_unassigned_variable(assignment)
        # Get an ordering of the values.
        ordered_values = self.domains[var]

        # Continue the backtracking recursion using |var| and |ordered_values|.
        if not self.ac3:
            # When arc consistency check is not enabled.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    del assignment[var]
        else:
            # Arc consistency check is enabled.
            # Problem 1c: skeleton code for AC-3
            # You need to implement arc_consistency_check().
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    # create a deep copy of domains as we are going to look
                    # ahead and change domain values
                    localCopy = copy.deepcopy(self.domains)
                    # fix value for the selected variable so that hopefully we
                    # can eliminate values for other variables
                    self.domains[var] = [val]

                    # enforce arc consistency
                    self.arc_consistency_check(var)

                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    # restore the previous domains
                    self.domains = localCopy
                    del assignment[var]

    def get_unassigned_variable(self, assignment):
        """
        Given a partial assignment, return a currently unassigned variable.

        @param assignment: A dictionary of current assignment. This is the same as
            what you've seen so far.

        @return var: a currently unassigned variable.
        """

        if not self.mcv:
            # Select a variable without any heuristics.
            for var in self.csp.variables:
                if var not in assignment: return var
        else:
            # Problem 1b
            # Heuristic: most constrained variable (MCV)
            # Select a variable with the least number of remaining domain values.
            # Hint: given var, self.domains[var] gives you all the possible values
            # Hint: get_delta_weight gives the change in weights given a partial
            #       assignment, a variable, and a proposed value to this variable
            # Hint: for ties, choose the variable with lowest index in self.csp.variables
            # BEGIN_YOUR_CODE (our solution is 7 lines of code, but don't worry if you deviate from this)
            min_num = float("inf")
            min_var = self.csp.variables[0]
            num = 0
            for var in self.csp.variables:
                num = 0
                if var not in assignment:
                    values = self.domains[var]
                    for value in values:
                        if self.get_delta_weight(assignment, var, value) != 0:
                            num = num+1
                    if num < min_num:
                        min_num = num
                        min_var = var
            return min_var
            # END_YOUR_CODE

    def arc_consistency_check(self, var):
        """
        Perform the AC-3 algorithm. The goal is to reduce the size of the
        domain values for the unassigned variables based on arc consistency.

        @param var: The variable whose value has just been set.
        """
        # Problem 1c
        # Hint: How to get variables neighboring variable |var|?
        # => for var2 in self.csp.get_neighbor_vars(var):
        #       # use var2
        #
        # Hint: How to check if a value or two values are inconsistent?
        # - For unary factors
        #   => self.csp.unaryFactors[var1][val1] == 0
        #
        # - For binary factors
        #   => self.csp.binaryFactors[var1][var2][val1][val2] == 0
        #   (self.csp.binaryFactors[var1][var2] returns a nested dict of all assignments)

        # BEGIN_YOUR_CODE (our solution is 20 lines of code, but don't worry if you deviate from this)
        variables = [var]
        while len(variables) > 0:
            var1 = variables.pop(0)
            for var2 in self.csp.get_neighbor_vars(var1):
                remove_vals = []
                for val2 in self.domains[var2]:
                    should_remove = 1
                    for val1 in self.domains[var1]:
                        if self.csp.binaryFactors[var1][var2][val1][val2] != 0:
                            should_remove = 0
                    if should_remove == 1:
                        remove_vals.append(val2)
                curr_domain = self.domains[var2]
                new_domain = []
                pruned_domain = 0
                for val in curr_domain:
                    if val not in remove_vals:
                        new_domain.append(val)
                    else:
                        pruned_domain = 1
                self.domains[var2] = new_domain
                if pruned_domain:
                    # add all of its neighbors
                    variables.append(var2)
        # END_YOUR_CODE




def find_travel_time(a_latitude, a_longitude, b_latitude, b_longitude):
	return util.haversine_miles(a_latitude, a_longitude, b_latitude, b_longitude)

def find_travel_time_geopy(a_latitude, a_longitude, b_latitude, b_longitude):
    coords_1 = (a_latitude, a_longitude)
    coords_2 = (b_latitude, b_longitude)
    distance = geopy.distance.vincenty(coords_1, coords_2).miles
    return distance*time_per_mile

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
    return haversine(lat1, lon1, lat2, lon2) * 0.62137119 * time_per_mile


def get_sum_variable(csp, name, variables, maxSum, factor, increment):
    domain = [(a, b) for a in range(0, maxSum + 1, increment) for b in range(0, maxSum + 1, increment)]
    result = ('sum', name, 'aggregated')
    csp.add_variable(result, [a for a in range(0, maxSum + 1, increment)])

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

    def __init__(self, activities, profile):
        self.activities = activities[profile.genre] # dict
        self.profile = profile
        self.num_slots = 11 # always keep this odd!
        self.max_travel_time = 60 #mins
        self.home = activities['home'] #dict 
        self.restaraunts = activities['food']
        self.act_and_rest = dict(activities[profile.genre])
        self.act_and_rest.update(self.restaraunts)
        print "max travel time is ", self.max_travel_time


    def get_activity_by_key(self, key):
        return self.activities[self.genre][key]

    def add_variables(self, csp, user_long, user_lat):
        print "starting add variables"
        time_domain = []
        for x in range(0, self.max_travel_time+1, 10):
            time_domain.append(x)
        # print time_domain
        activities_domain = list(self.activities.keys())
        home_domain = list(self.home.keys())
        restaraunts_domain = list(self.restaraunts.keys())
        lunch = 4
        dinner = 8
        
        # slots (including the travel time)
        for i in range(0, self.num_slots):
            if i == 0 or i == self.num_slots - 1:
                csp.add_variable(i, home_domain)
                continue
            if i == lunch or i == dinner:
                csp.add_variable(i, restaraunts_domain)
                continue
            if i % 2 == 0:
                # activity
                csp.add_variable(i, activities_domain) # if an activity/restaraunt slot is not assigned
            else:
                # travel time
                csp.add_variable(i, time_domain)
        print "ending add variables"
    
    # budget: value of (i, "activity") summed up less than user budget
    def add_budget_constraints(self, csp):
        print "starting add budget constraints"
        def factor(a, b):
            val = int(math.ceil(self.act_and_rest[a].cost / 10)) * 10 + 10
            return b[1] == b[0] + val

        variables = []
        for i in range(0, self.num_slots):
            if i % 2 == 0 and i != 0 and i != self.num_slots - 1:
                variables.append(i)

        result = get_sum_variable(csp, "budget", variables, self.profile.budget, factor, 10)
        csp.add_unary_factor(result, lambda val: val <= self.profile.budget)
        print "ending add budget constraints"

    # time: value of (i, "activity").duration and (i, "travel").duration summed up less than user time
    # def add_time_constraints(self, csp):
    #     print "starting time constaints"
    #     def activity_factor(a, b):
    #         val = int(math.ceil(self.activities[a].duration / 10)) * 10
    #         return b[1] == b[0] + val

    #     def time_factor(a, b):
    #         return b[1] == b[0] + a

    #     activity_variables = []
    #     time_variables = []
    #     for i in range(0, self.num_slots):
    #         if i % 2 == 0 and i != 0 and i != self.num_slots-1:
    #             activity_variables.append(i)
    #         if i % 2 != 0 and i != 0 and i != self.num_slots-1:
    #             time_variables.append(i)
    #     result1 = get_sum_variable(csp, "act_time", activity_variables, self.profile.total_time, activity_factor, 10)
    #     result2 = get_sum_variable(csp, "travel_time", time_variables, self.profile.total_time, time_factor, 10)
    #     csp.add_binary_factor(result1, result2, lambda val1, val2: val1 + val2 <= self.profile.total_time)
    #     print "ending time contraints"

    # constraint to make activities different in a schedule
    def add_different_activity_constraints(self, csp):
        print "starting add_different_activity_constraints"
        def factor(a, b):
            return a != b

        # not adding the last variable since it will be home
        variables = [(i, j) for i in range(0, self.num_slots-1) for j in range(0, self.num_slots-1) if i != j and i % 2 == 0 and j % 2 == 0]
        for i, j in variables:
            csp.add_binary_factor(i, j, factor)

        print "ending add_different_activity_constraints"

    # travel time: unary factor where for each (i, "travel") if less time, then greater weight and vice versa
    # def add_weighted_travel_time_constraints(self, csp):
    #     print "starting add weighted travel time constaints"
    #     for i in range(0, self.num_slots):
    #         if i % 2 != 0:
    #             def factor(a):
    #                 if a == 0: return .9
    #                 return 1/a
    #             csp.add_unary_factor(i, factor)
    #     print "ending add weighted travel time constaints"

    # food: sum number of activities that have food, and if they want food it has to equal one or else 0
    # def add_food_constraints(self, csp):
    #     print "starting add food constaints"
    #     def factor(a, b):
    #         val = self.activities[a].is_food
    #         return b[1] == b[0] + val

    #     num_restaraunts = self.profile.want_food
    #     variables = []
    #     for i in range(0, self.num_slots):
    #         if i != 0 and i != self.num_slots-1 and i % 2 == 0:
    #             variables.append(i)
        
    #     result = get_sum_variable(csp, "food", variables, num_restaraunts, factor, 1)
    #     csp.add_unary_factor(result, lambda val: val == num_restaraunts)
    #     print "ending add food constaints"

    # travel time: binary factor where for each travel slot, travel_time(prev_activity, next_activity) = travel_time, set (i, "travel") equal to that
    def add_slot_travel_time_constraints(self, csp):
        print "starting add travel time constraints"
        for i in range(1, self.num_slots):
            if i % 2 != 0 and i != self.num_slots:
                def factor_duration(a, b, c):
                    if a == -1:
                        return b == int(math.ceil(haversine_miles(self.home[a].latitude, self.home[a].longitude, self.act_and_rest[c].latitude, self.act_and_rest[c].longitude) / 10)) * 10 + 10
                    if c == -1:
                        return b == int(math.ceil(haversine_miles(self.act_and_rest[a].latitude, self.act_and_rest[a].longitude, self.home[c].latitude, self.home[c].longitude) / 10)) * 10 + 10
                    else:
                        return b == int(math.ceil(haversine_miles(self.act_and_rest[a].latitude, self.act_and_rest[a].longitude, self.act_and_rest[c].latitude, self.act_and_rest[c].longitude) / 10)) * 10 + 10
                print i
                csp.add_ternary_factor(i-1, i, i+1, factor_duration)
        print "ending add travel time constraints"

    # rating: for the value of each (i, "activity"), we give a higher weight for a better rating, UNARY FACTOR
    def add_rating_constraints(self, csp):
        print "starting add rating constaints"
        for i in range(1, self.num_slots-1):
            if i % 2 == 0:
                def factor(a):
                    return self.act_and_rest[a].rating/5
                csp.add_unary_factor(i, factor)
        print "ending add travel time constraints"

    def add_review_count_constraints(self, csp):
        print "starting add review count constraints"
        for i in range(1, self.num_slots-1):
            if i % 2 == 0:
                def factor(a):
                    if a is None:
                        return 1
                    num_reviews = self.act_and_rest[a].review_count
                    if num_reviews == 0:
                        return .5
                    # Return log base 10 of number of reviews
                    # TODO: look into playing around with this normalization factor
                    return math.log(num_reviews, 10) + 1
                csp.add_unary_factor(i, factor)
        print "ending add review count constraints"

    # def add_penalize_none_constraints(self, csp):
    #     print "starting add_penalize_none_constraints"
    #     for i in range(1, self.num_slots):
    #         def factor(a):
    #             if a is None:
    #                 return 0.2
    #             return 1
    #         csp.add_unary_factor(i, factor)
    #     print "ending add_penalize_none_constraints"

    def get_basic_csp(self):
        """
        Return a CSP that only enforces the basic budget constraints

        @return csp: A CSP where basic variables and constraints are added.
        """
        csp = util.CSP()
        self.add_variables(csp, self.profile.user_latitude, self.profile.user_longitude)
        self.add_budget_constraints(csp)
        self.add_different_activity_constraints(csp)
        self.add_rating_constraints(csp)
        # self.add_food_constraints(csp)
        self.add_review_count_constraints(csp)
        self.add_slot_travel_time_constraints(csp)

        # self.add_time_constraints(csp)
        # self.add_weighted_travel_time_constraints(csp)
        # self.add_penalize_none_constraints(csp)
        return csp
