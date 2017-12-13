#!/usr/bin/python
import sys
import argparse
import json
import random
from final_project import util

# Coordinates of Stanford University Tresidder Parking Lot
DEFAULT_LAT = 37.42358
DEFAULT_LONG = -122.170733

DEFAULT_BUDGET = 100
DEFAULT_START = 9
DEFAULT_END = 17
DEFAULT_GENRE = "all"

# Names of files storing businesses under each category
GENRE_FILES = {
  "thrill": "thrill.json",
  "intellect": "intellect.json",
  "outdoors": "outdoors.json",
  "all": "all.json"
}
# Name of file storing restaurant info
RESTAURANT_FILE = "restaurants.json"

# Price estimates
DEFAULT_PRICE = 40
PRICE_RANGE = {
  "$": 10,
  "$$": 30,
  "$$$": 60,
  "$$$$": 100
}

DEFAULT_DURATION = 1
DEFAULT_TRAVEL_TIME = .5

def get_price(business):
  """ Returns price estimate of business
  """
  if 'price' in business and business['price'] in PRICE_RANGE:
    return PRICE_RANGE[business['price']]
  return DEFAULT_PRICE

def get_travel_time(business, start_lat, start_long):
  """ Returns num hours needed to travel to business
  """
  lat_coord = business["coordinates"]["latitude"]
  long_coord = business["coordinates"]["longitude"]
  if lat_coord and long_coord and start_lat and start_long:
    # 30 minutes for every .1 coordinate change
    return (abs(lat_coord - start_lat) + abs(long_coord - start_long)) /.1 * .5
  return DEFAULT_TRAVEL_TIME

def get_duration(business):
  """ Returns num hours typically spent at the business
  """
  return DEFAULT_DURATION

def load_businesses(filename):
  """ Loads businesses from file into set
  """
  businesses = []
  with open(filename, 'r') as businessfile:
    for b in businessfile:
      businesses.append(json.loads(b))
  return businesses


def get_activity(businesses, constraints, itinerary):
  """ Returns first activity that matches constraints
  """
  for i in range(len(businesses)):
    b = random.choice(businesses)
    if (get_price(b) < constraints["moneyLeft"] and
      get_travel_time(b, constraints["lat"], constraints["long"]) +
        get_duration(b) <= constraints["timeLeft"] and
        b not in itinerary):
      return b
  return None

def get_constraints(prefs):
  """ Gets initial constraints for activity based on user preferences
  """
  if prefs.end - prefs.start < 0:
    print "ERROR: START TIME MUST BE LESS THAN END TIME"
    sys.exit(0)
  return {
    "lat": prefs.latitude,
    "long": prefs.longitude,
    "moneyLeft": prefs.budget,
    "timeLeft": prefs.end - prefs.start,
    "genre": prefs.genre
  }

def update_constraints(old_constraints, activity):
  """ Update constraints with activity chosen
  """
  return {
    "lat": activity["coordinates"]["latitude"],
    "long": activity["coordinates"]["longitude"],
    "moneyLeft": old_constraints["moneyLeft"] - get_price(activity),
    "timeLeft": (old_constraints["timeLeft"]
      - get_duration(activity)
      - get_travel_time(activity, old_constraints["lat"], old_constraints["long"]))
  }

def create_itinerary(prefs, businesses, restaurants):
  """ Returns array of activities based on user preferences and
  avalaible businesses and restaurants
  """
  constraints = get_constraints(prefs)
  itinerary = []
  food = prefs.food
  while constraints['timeLeft'] > 0:
    activity = None
    if food:
      activity = get_activity(restaurants, constraints, itinerary)
    else:
      activity = get_activity(businesses, constraints, itinerary)
    if activity:
      if prefs.verbose:
        print ""
        print "Activity found"
        print "constraints: " + str(constraints)
        print "activity found with above constraints: " + str(activity), prefs
        print "activity duration: " + str(get_duration(activity))
        print "activity traveltime: " + str(get_travel_time(activity, constraints["lat"], constraints["long"]))
        print "activity price: " + str(get_price(activity))
      itinerary.append(activity)
      constraints = update_constraints(constraints, activity)
    else:
      if prefs.verbose:
        print ""
        print "No activity found with constraints: " + str(constraints)
      break
  return itinerary

def print_itinerary(itinerary):
  """ Pretty prints itinerary
  """
  print ""
  if not itinerary:
    print "Sorry, no valid itinerary was found."
    return
  print "Itinerary found with " + str(len(itinerary)) + " activities: "
  for i, activity in enumerate(itinerary):
    print "  ", str(i+1) + ")", activity["name"]
    print "    rating:", activity["rating"]
    print "    review_count:", activity["review_count"]

    print "    address:", " ".join(i for i in activity["location"]["display_address"])

def get_args():
  """ Parses command line arguments.
  Run 'python create_itinerary -h' for available flags
  """
  parser = argparse.ArgumentParser(
    description="Outputs an itinerary of activities based on user preferences")
  parser.add_argument("-v", "--verbose", action="store_true", help="print helpful status and debug statements")
  parser.add_argument("-f", "--food", action="store_true", help="whether itinerary should include food")
  parser.add_argument("-lat", "--latitude", type=float, default=DEFAULT_LAT, help="starting latitude coordinate")
  parser.add_argument("-long", "--longitude", type=float, default=DEFAULT_LONG, help="starting longitude coordinate")
  parser.add_argument("-b", "--budget", type=int, default=DEFAULT_BUDGET, help="maximum amount of money to spend")
  parser.add_argument("-g", "--genre", choices=GENRE_FILES.keys(), default=DEFAULT_GENRE, help="type of itinerary to plan")
  parser.add_argument("-a", "--activities", help="filename from which to load activities")
  parser.add_argument("-r", "--restaurants", help="filename from which to load restaurants")
  
  hoursOfDay = range(0, 24)
  parser.add_argument("-s", "--start", type=int, default=DEFAULT_START, choices=hoursOfDay, help="starting hour (in 24-hour clock)")
  parser.add_argument("-e", "--end", type=int, default=DEFAULT_END, choices=hoursOfDay, help="ending hour (in 24-hour clock)")
  return parser.parse_args()

def main():
  """ Takes user preferences from command line arguments,
  loads businesses and creates itinerary from user preferences and
  available businesses
  """
  prefs = get_args()
  if prefs.verbose:
    print "User Preferences"
    print "  Food: " + ("yes" if prefs.food else "no")
    print "  Starting coordinates: " + str(prefs.latitude) + ", " + str(prefs.longitude)
    print "  Bugdet: " + str(prefs.budget)
    print "  Start time: " + str(prefs.start)
    print "  End time: " + str(prefs.end)
  
  businesses = load_businesses(prefs.activities or GENRE_FILES[prefs.genre])
  restaurants = (load_businesses(prefs.restaurants or RESTAURANT_FILE)
    if prefs.food else None)
  for i in range(0,100):
    itinerary = create_itinerary(prefs, businesses, restaurants)
    #print_itinerary(itinerary)
    score = util.ScheduleScore(itinerary, baseline=True, food = True)
    #print "Itinerary rank = ", 
    print score.get_schedule_score()

if __name__ == "__main__":
    main()
