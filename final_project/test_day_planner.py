import util, submission, sys

if len(sys.argv) < 2:
    print "Usage: %s <profile file (e.g., profile3d.txt)>" % sys.argv[0]
    sys.exit(1)

profilePath = sys.argv[1]
profile = util.Profile(profilePath)
profile.print_info()
# genreToPath = {'indoors':'../intellect.json','food':'../restaurants.json','outdoors':'../outdoors.json','thrill':'../thrill.json'}
genreToPath = {'thrill':'../activities_short.json','food':'../restaurants_short.json'}
activities = util.ActivityCollection(profile, genreToPath).activities
cspConstructor = submission.SchedulingCSPConstructor(activities, profile)
csp = cspConstructor.get_basic_csp()
# cspConstructor.add_all_additional_constraints(csp)
alg = submission.BacktrackingSearch()
alg.solve(csp, mcv = True, ac3 = True, max_num_assignments = 10)
util.print_all_scheduling_solutions(alg.allAssignments, profile, activities)

print "optimal solution"
util.print_scheduling_solution(alg.optimalAssignment, profile, activities)

# if alg.numOptimalAssignments > 0:
#     solution = util.extract_course_scheduling_solution(profile, alg.optimalAssignment)
#     util.print_course_scheduling_solution(solution)
