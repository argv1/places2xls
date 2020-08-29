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
from pathlib import Path
import pgeocode
import pprint
import time
import xlsxwriter

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
    Request places and use the place ids to return the details for each place
    '''
    stored_results = []
    n, c = 0, 0

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
                print("There are not that many places in the reqeusted area.")
                break

        # if verbosity is true, print out the place
        if verbose:
            pprint.pprint(places_result['results'])

        # Loop through each of the places in the results, and get the place details.      
        for place in places_result['results']:

            # break the loop if requested amount of results are reached
            if n >= n_res:
                break

            # Use the place id to request detailed informations
            places_details = gmaps.place(place_id= place['place_id'], fields=details)
            
            # check if any of the requested details has no value
            invalid_res = False
            if len(details) > len(places_details['result']):
                invalid_res = True

            # if strict level is high, filter out places from other cities/zipcode
            if not invalid_res and (strict == 0 or (strict == 1 and city in places_details['result']['formatted_address']) or (strict == 2 and zipcode in places_details['result']['formatted_address'])):
                
                # Store the details
                stored_results.append(places_details['result'])

                if verbose:
                    pprint.pprint(places_details['result']) 

                n+=1
            c+=1

    return stored_results

def xls(stored_results):
    '''
    Converting the results to an excel spreadsheet.
    '''

    # Define path and filename
    base_path       = Path('H:\OneDrive\Programme\_current\places2xls')  #adjust
    download_files  = base_path / 'data.xlsx'            

    # Define the headers, that is just the key of each result dictionary.
    row_headers = stored_results[0].keys()
    
    # Create a new workbook and a new worksheet.
    workbook = xlsxwriter.Workbook(download_files)
    worksheet = workbook.add_worksheet()

    # Populate the header row
    col = 0
    for column in row_headers:
        worksheet.write(0, col, column)
        col += 1

    row = 1
    col = 0
    # Populate the other rows

    # Get each result from the list.
    for result in stored_results:

        # Get the values from each result.
        result_values = result.values()

        # Loop through each value in the values component.
        for value in result_values:
            worksheet.write(row, col, value)
            col += 1
        
        # Make sure to go to the next row & reset the column.
        row += 1
        col = 0

    # Close the workbook
    workbook.close()

def main():
    # Initiate the parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', help='Enter type of place', type=str, required=True)
    parser.add_argument('-z', '--zip', help='Enter zipcode', type=str, required=True)
    parser.add_argument('-c', '--countrycode', help='Enter two letter country code', type=str, default='DE')
    parser.add_argument('-d', '--details', help='Which details are required', type=str, default=['name', 'formatted_address', 'formatted_phone_number']) 
    parser.add_argument('-n', '--num', help='Enter number of entries', type=int, default='20')  
    parser.add_argument('-s', '--strict', help='0: places from other zipcode, 1: same city, 2: same zipcode', type=int, default='1')
    parser.add_argument('-v', '--verbose', help='Detailed output')
    args = parser.parse_args()

    latlng, city    = location(args.countrycode, args.zip)
    zipcode         = args.zip
    place_type      = args.type
    n_res           = args.num
    details         = args.details
    if "name" not in details: details.append("name")
    strict          = 0 if "formatted_address" not in details else args.strict
    verbose         = True if args.verbose else False
    
    # Get places
    stored_results = get_places(latlng, city, zipcode, place_type, n_res, details, strict, verbose)

    # Write information to excel
    xls(stored_results)

if __name__ == '__main__':
    main()