import util, submission, sys

if len(sys.argv) < 2:
    print "Usage: %s <profile file (e.g., profile3d.txt)>" % sys.argv[0]
    sys.exit(1)

profilePath = sys.argv[1]
profile = util.Profile(profilePath)
profile.print_info()
# genreToPath = {'indoors':'../intellect.json','food':'../restaurants.json','outdoors':'../outdoors.json','thrill':'../thrill.json'}
genreToPath = {'thrill':'../activities_100.json','food':'../restaurants_100.json'}
# genreToPath = {'thrill':'../activities_short.json','food':'../restaurants_short.json'}
activities = util.ActivityCollection(profile, genreToPath).activities
cspConstructor = submission.SchedulingCSPConstructor(activities, profile)
csp = cspConstructor.get_basic_csp()

def test_beamsearch(k):
  alg = submission.BeamSearch()
  k=100
  alg.solve(csp, mcv = True, ac3 = False, k = k)

  if alg.allAssignments:
    print "printing k=%d assignments found" % k
    util.print_all_scheduling_solutions_beam(alg.allAssignments, profile, activities)
  else:
    print "no solution found"
  return alg.allAssignments

def test_backtrack(max_num_assignments):
  alg = submission.BacktrackingSearch()
  alg.solve(csp, mcv = True, ac3 = False, max_num_assignments = max_num_assignments)
  if alg.allOptimalAssignments:
    print "all optimal assignments"
    util.print_all_scheduling_solutions(alg.allOptimalAssignments, profile, activities)
  else:
    print "no solution found"
  return alg.allOptimalAssignments

def test_icm(max_iterations, initial_assignment, gibbs_sampling):
  alg = submission.ICM()
  alg.solve(csp, max_iterations = max_iterations,
    initial_assignment = initial_assignment, gibbs_sampling = gibbs_sampling)
  if alg.optimalAssignment:
    print "printing solution"
    util.print_scheduling_solution(alg.optimalAssignment, profile, activities)
  else:
    print "no solution found"

# test_beamsearch(k = 100)
# test_backtrack(max_num_assignments = 100)
test_icm(100, None, False)
test_icm(100, None, True)