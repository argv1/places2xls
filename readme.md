![logo](https://github.com/argv1/places2xls/blob/master/img/logo.png)

## places2xls
======================

places2xls helps to extract places using the google places API and store them in an excel spreadsheet.

## Requirements
to install the required packages just use:
```python
pip3 install -r requirements.txt
```


## setup
1. Register for a free [Google Cloud Plattform Account](https://cloud.google.com/)
2. Enable google places API(https://console.cloud.google.com/apis/library) in order to receive your API key.


Enter this api key here:
```python
API_KEY = YOUR-API-KEY
```


## usage
After you entered the above information, run the main.py with at least the required arguments -t for type of business and -z for zipcode

Usage: main.py -c COUNTRYCODE -z ZIPCODE -t TYPE - n NUMBER_OF_RESULTS -s STRICTLVL -v -d DETAILS<p>
   i.e. main.py -c DE -z 50667 -t restaurant - n 40 -s 2 -v -d "name, formatted_address, website, opening_hours"

Use main.py -h for a list of all options


## License
This code is licensed under the [GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/). 
For more details, please take a look at the [LICENSE file](https://github.com/argv1/places2xls/blob/master/LICENSE).


## outlook
- Please feel free to enhance the script
