import util, submission, sys, time
from datetime import datetime


if len(sys.argv) < 2:
    print "Usage: %s <profile file (e.g., profile3d.txt)>" % sys.argv[0]
    sys.exit(1)

profilePath = sys.argv[1]
profile = util.Profile(profilePath)
profile.print_info()
# genreToPath = {'indoors':'../intellect.json','food':'../restaurants.json','outdoors':'../outdoors.json','thrill':'../thrill.json'}
genreToPath = {'thrill':'../all.json','food':'../restaurants.json'}
# genreToPath = {'thrill':'../activities_short.json','food':'../restaurants_short.json'}
activities = util.ActivityCollection(profile, genreToPath).activities
cspConstructor = submission.SchedulingCSPConstructor(activities, profile)
csp = cspConstructor.get_basic_csp()
# cspConstructor.add_all_additional_constraints(csp)
alg = submission.BeamSearch()
k=200
alg.solve(csp, mcv = True, ac3 = False, k = k)

if alg.allAssignments:
  print "printing k=%d assignments found" % k
  util.print_all_scheduling_solutions_beam(alg.allAssignments, profile, activities)
else:
  print "no solution found"

