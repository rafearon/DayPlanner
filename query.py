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

LOCATIONS = ["San Francisco, CA", "Oakland, CA", "Berkeley, CA", "Pacifica, CA", "South San Francisco, CA", "San Mateo, CA", "Redwood City, CA", "Mountain View/Sunnyvale, CA", "San Jose, CA", "Santa Cruz, CA", "Fremont, CA", "Morgan Hills, CA", "Pescadero, CA","Half Moon Bay, CA"]


GENRE_FILES = {
  "thrill": "thrill.json",
  "intellect": "intellect.json",
  "outdoors": "outdoors.json",
  "all": "business.json"
}

INDOORSY = [
'aquariums',
'lasertag',
'bowling',
'skatingrinks',
'arcades',
'galleries',
'movietheaters',
'eatertainment',
'jazzandblues',
'museums',
'observatories',
'theater',
'planetarium',
'spas'
]


THRILL = [
'amusementparks',
'bungeejumping',
'freediving',
'scuba',
'escapegames',
'experiences',
'gokarts',
'hanggliding',
'hot_air_balloons',
'jetskis',
'kiteboarding',
'mountainbiking',
'paddleboarding',
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
'hauntedhouses'
]

OUTDOORSY [
'beaches',
'boating',
'bocceball',
'bubblesoccer',
'hiking',
'gardens',
'farms'
]



        

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
                    results.add(json.dumps(business))
                    #out.write(json.dumps(business))
                    #out.write("\n")
            else:
                break
    #print(results)
    return results
 
            
def print_queries(category, term, businesses):
        with open(term+".json", 'a') as out:
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
            
                



def main():
    restaurant = 'restaurant'
    category = ''
    terms = [restaurant]
    termDirectory = multi_query_business(terms, LOCATIONS)
    print_queries(category, restaurant, termDirectory[restaurant])
    

if __name__ == '__main__':
    main()