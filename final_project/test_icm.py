import util, submission, sys

if len(sys.argv) < 2:
    print "Usage: %s <profile file (e.g., profile3d.txt)>" % sys.argv[0]
    sys.exit(1)

profilePath = sys.argv[1]
profile = util.Profile(profilePath)
profile.print_info()
# genreToPath = {'indoors':'../intellect.json','food':'../restaurants.json','outdoors':'../outdoors.json','thrill':'../thrill.json'}
genre = 'thrill'
genreToPath = {genre:'../activities_100.json','food':'../restaurants_100.json'}
#genreToPath = {'thrill':'../activities_short.json','food':'../restaurants_short.json'}
activities = util.ActivityCollection(profile, genreToPath).activities
cspConstructor = submission.SchedulingCSPConstructor(activities, profile)
csp = cspConstructor.get_basic_csp()
# cspConstructor.add_all_additional_constraints(csp)
alg = submission.ICM()
alg.solve(csp, max_iterations = 100, gibbs_sampling = False, initial_assignment = None)
if alg.optimalAssignment:
  print "printing solution"
  util.print_scheduling_solution(alg.optimalAssignment, profile, activities)
else:
  print "no solution found"
