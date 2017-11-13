# -*- coding: utf-8 -*-
#https://github.com/Yelp/yelp-fusion/tree/master/fusion/python
"""

"""
from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib


# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


# OAuth credential placeholders that must be filled in by users.
# You can find them on
# https://www.yelp.com/developers/v3/manage_app
CLIENT_ID = 'Ac1Jga9ln_zF96nUd9t7WA'
CLIENT_SECRET = 'g0GpLol6MqLMmlK8VBN7NugCESD3yqNWAZz2FnslxEC6lTmxSvwPQcdce1BapeVF'


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'


# Defaults for our simple example.
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 1000
BLOCK_LIMIT = 50

LOCATIONS = ["San Francisco, CA", "Oakland, CA", "Berkeley, CA", "Pacifica, CA", "South San Francisco, CA", "San Mateo, CA", "Redwood City, CA", "Mountain View, CA", "Sunnyvale, CA", "San Jose, CA", "Santa Cruz, CA", "Fremont, CA", "Morgan Hills, CA", "Pescadero, CA","Half Moon Bay, CA"]


GENRE_FILES = {
  "thrill": "thrill.json",
  "intellect": "intellect.json",
  "outdoors": "outdoors.json",
  "all": "business.json",
  "restaurants": "restaurants.json"
}

GENRES = ('thrill', 'intellect', 'outdoors', 'restaurants')

INTELLECT = [
'aquariums',
'laser tag',
'bowling',
'skating rinks',
'arcades',
'galleries',
'movie theaters',
'eatertainment',
'jazz and blues',
'museums',
'observatories',
'theater',
'planetarium',
'spas',
'concerts',
'shopping',
'malls'
]


THRILL = [
'amusement parks',
'bungee jumping',
'free diving',
'scuba',
'escape games',
'experiences',
'go karts',
'hang gliding',
'hot air balloons',
'jet skis',
'kite boarding',
'mountain biking',
'paddle boarding',
'paintball',
'parasailing',
'rafting',
'skiing',
'skydiving',
'sledding',
'snorkeling',
'surfing',
'tubing',
'zorbing',
'haunted houses',
'sports'
]

OUTDOORS = [
'beaches',
'boating',
'bocceball',
'bubble soccer',
'hiking',
'gardens',
'farms',
'parks',
'monuments'
]

RESTAURANTS = [
'restaurants',
'bars'
]



def find_genre_by_term(term):
    if term in RESTAURANTS:
        return 'restaurants'
    elif term in OUTDOORS:
        return 'outdoors'
    elif term in THRILL:
        return 'thrill'
    elif term in INTELLECT:
        return 'intellect'


def get_genre_terms(genre):
    if genre == 'thrill':
        return THRILL
    elif genre == 'outdoors':
        return OUTDOORS
    elif genre == 'intellect':
        return INTELLECT
    elif genre == 'restaurants':
        return RESTAURANTS
    elif genre == 'all_no_restaurants':
        return list(set(THRILL).union(set(OUTDOORS)).union(set(INTELLECT)))
    else:
        all_genres = set(THRILL).union(set(OUTDOORS)).union(set(INTELLECT)).union(set(RESTAURANTS))
        return list(all_genres)



def avg_time_by_genre(genre, business):
    if genre == 'restaurants':
        return restaurant_avg_time(business)
    elif genre == 'thrill':
        return 120
    elif genre == 'outdoors':
        return 180
    elif genre == 'intellect':
        return 100



def restaurant_avg_time(business):
    if "price" not in business:
        return 30
    price = business["price"]
    if price == "$":
        return 20
    elif price == "$$":
        return 30
    elif price == "$$$":
        return 60
    elif price == "$$$$":
        return 120


def obtain_bearer_token(host, path):
    """Given a bearer token, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        str: OAuth bearer token, obtained using client_id and client_secret.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    assert CLIENT_ID, "Please supply your client_id."
    assert CLIENT_SECRET, "Please supply your client_secret."
    data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
    })
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    return bearer_token


def request(host, path, bearer_token, url_params=None):
    """Given a bearer token, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % bearer_token,
    }

    #print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(bearer_token, term, location, offset):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': BLOCK_LIMIT,
        'offset': offset,
        'radius': 40000,
        'sort_by': 'rating'
    }
    #print(url_params)
    return request(API_HOST, SEARCH_PATH, bearer_token, url_params=url_params)


def get_business(bearer_token, business_id):
    """Query the Business API by a business ID.

    Args:
        business_id (str): The ID of the business to query.

    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, bearer_token)


def query_api(term, location):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)

    results = set()
    print("Querying Yelp with term = " + term +" , location = " + location)
    #with open(term+"-businesses.txt", 'w') as out:
    for offset in range(0, SEARCH_LIMIT, 50):
            response = search(bearer_token, term, location, offset)
            businesses = response.get('businesses')
            #print(response)
            #print businesses
            #print offset
            
            if businesses:
                for business in businesses:
                    business_id = business['id']
                    #business_details = get_business(bearer_token, business_id)
                    business_dict = json.loads(json.dumps(business))
                    del business_dict['distance']
                    genre = find_genre_by_term(term)
                    time_spent_min = avg_time_by_genre(genre, business)
                    business_dict['time_spent_minutes'] = time_spent_min
                    results.add(json.dumps(business_dict))
                    #out.write(json.dumps(business))
                    #out.write("\n")
            else:
                break
    #print(results)
    return results
 
            
def write_results_to_file(category, term, businesses):
        with open(category+".json", 'a') as out:
            for item in businesses:
                out.write(item)
                out.write("\n")


#Input: array of search terms, array of locations
#Output: Dictionary of [term: set(business)]. Each set(business) aggregates businesses for all locations
def multi_query_business(terms, locations):
    termDirectory = {}
    for term in terms:
        termBusinesses = set()
        for location in locations:
            termBusinesses = termBusinesses.union(query_api(term, location))
            
                

        termDirectory[term] = termBusinesses
    return termDirectory


def remove_duplicates(genre):
    with open(category+".json", 'a') as out:
            for item in businesses:
                out.write(item)
                out.write("\n")
            



                



def main():
    all_terms = get_genre_terms("all")
    termDirectory = multi_query_business(all_terms, LOCATIONS)
    for term in all_terms:
        write_results_to_file('all', term, termDirectory[term])
    for genre in GENRES:
        terms_in_genre = get_genre_terms(genre)
        output_set = set()
        for term in terms_in_genre:
            businesses = termDirectory[term]
            for business in businesses:
                output_set.add(business)
        with open(genre+".json", "a") as out:
            for item in output_set:
                out.write(item)
                out.write("\n")

    

if __name__ == '__main__':
    main()