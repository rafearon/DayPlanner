import util, submission, sys

if len(sys.argv) < 2:
    print "Usage: %s <profile file (e.g., profile3d.txt)>" % sys.argv[0]
    sys.exit(1)

profilePath = sys.argv[1]
# genreToPath = {'indoors':'../intellect.json','food':'../restaurants.json','outdoors':'../outdoors.json','thrill':'../thrill.json'}
genreToPath = {'thrill':'../activities_short.json','food':'../restaurants_short.json'}
activities = util.ActivityCollection(genreToPath).activities
profile = util.Profile(profilePath)
profile.print_info()
cspConstructor = submission.SchedulingCSPConstructor(activities, profile)
csp = cspConstructor.get_basic_csp()
# cspConstructor.add_all_additional_constraints(csp)
alg = submission.BacktrackingSearch()
print "starting backtracking search"
alg.solve(csp, mcv = False, ac3 = False)
print "solved backtracking search"
if alg.optimalAssignment:
    print alg.optimalWeight
    for key, value in alg.optimalAssignment.items():
        print key, '=', value

# if alg.numOptimalAssignments > 0:
#     solution = util.extract_course_scheduling_solution(profile, alg.optimalAssignment)
#     util.print_course_scheduling_solution(solution)
