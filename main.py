#!/usr/bin/env python3
'''
    small script to scrap google places and export to excel 
    (https://github.com/argv1/places2xls/)

    Usage: main.py -c COUNTRYCODE -z ZIPCODE -t TYPE - n NUMBER_OF_RESULTS -s STRICTLVL -v VERBOSITY -d DETAILS
    i.e. main.py -c DE -z 50667 -t restaurant - n 40 -s 2 -v -d "name, formatted_address, website, opening_hours"
    places types: https://developers.google.com/places/supported_types

    please feel free to improve
'''

import argparse
import googlemaps
import pandas as pd
from   pathlib import Path
import pgeocode
import time

# Define API Key
API_KEY = 'YOUR-GOOGLE-API-KEY'

# Define Client
gmaps = googlemaps.Client(key=API_KEY)

def location(country, zip):
    '''
    Returns the latitude, longitude of the entered zipcode/country
    '''
    nomi = pgeocode.Nominatim(country)
    query_res = nomi.query_postal_code(zip)
    return(f"{str(query_res.latitude)},{str(query_res.longitude)}", query_res.place_name)

def get_places(latlng, city, zipcode, place_type, n_res, details, strict, verbose):
    '''
    Request places, use the place ids to return the details for 
    each place and save the collected information to an excel spreadsheet
    '''
    n, c, d = 0, 0, 0
    df = pd.DataFrame(columns=details)
    
    # Define our Search
    places_result = gmaps.places_nearby(location=latlng, radius=4_000, language='de', type=place_type)

    while n <  n_res:       
        # get next 20 results if the last are processed and more are needed
        if c%20 == 0:
            # sleep to ensure the pake token is known by the google api already
            time.sleep(5)

            try:
                places_result  = gmaps.places_nearby(page_token = places_result['next_page_token'])
            except:
                print("There are not that many places in the requested area.")
                break

        # Loop through each of the places in the results, and get the place details.      
        for place in places_result['results']:
            
            # break the loop if requested amount of results are reached
            if n >= n_res:
                break

            # Use the place id to request detailed informations
            places_details = gmaps.place(place_id= place['place_id'], fields=details)
            
            # check if any of the requested details has no value
            valid_res = True
            if len(details) > len(places_details['result']):
                valid_res = False

            # if strict level is high, filter out places from other cities/zipcode
            if valid_res and (strict == 0 or (strict == 1 and city in places_details['result']['formatted_address']) or (strict == 2 and zipcode in places_details['result']['formatted_address'])):
                
                # Store the details
                for entry in places_details['result']:
                    df.at[n, entry] = places_details['result'][entry]
                    
                n+=1
            else:
                d+=1
            c+=1

    if verbose:
        print(f'{df}\n\n{c} entries viewed.\n{d} entries dropped.')

    # Define path and filename
    base_path       = Path('H:\OneDrive\Programme\_current\places2xls')  #adjust
    workbook_file   = base_path / 'data.xlsx'            

    # Write excel file
    df.to_excel(workbook_file, index=False) 

def main():
    # Initiate the parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', help='Enter type of place', type=str, required=True)
    parser.add_argument('-z', '--zip', help='Enter zipcode', type=str, required=True)
    parser.add_argument('-c', '--countrycode', help='Enter two letter country code', type=str, default='DE')
    parser.add_argument('-d', '--details', help='Which details are required', type=str, default=['name', 'formatted_address', 'formatted_phone_number']) 
    parser.add_argument('-n', '--num', help='Enter number of entries', type=int, default='20')  
    parser.add_argument('-s', '--strict', help='0: places from other zipcode, 1: same city, 2: same zipcode', type=int, default='1')
    parser.add_argument('-v', '--verbose', help='Enables detailed output', action='store_const', const=True)
    args = parser.parse_args()

    latlng, city    = location(args.countrycode, args.zip)
    zipcode         = args.zip
    place_type      = args.type
    n_res           = args.num
    if "name" not in args.details: details = ["name"] + args.details
    else:  details = args.details
    strict          = 0 if "formatted_address" not in details else args.strict
    verbose         = True if args.verbose else False
    
    # Get places and write them to excel
    get_places(latlng, city, zipcode, place_type, n_res, details, strict, verbose)

if __name__ == '__main__':
    main()
