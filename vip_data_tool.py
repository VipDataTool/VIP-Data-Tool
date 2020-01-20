"""
MIT License  

Copyright (c) 2019 Eric Ostrander

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import foursquare
import traceback
import censusdata
import pickle
import json
from pathlib import Path
from geopy.geocoders import Nominatim
import pandas as pd 
import scipy.stats
import requests
import folium
import numpy as np
# import datetime

print("All dependencies imported successfully!")


__version__ = '0.9.0'


class VipDt:
    """
    A collection of methods for returning venue data for 
    a given address from the Foursquare Places API.

    Parameters
    ----------
    address: str
      A real address for a particular location

    credentials: dict
      Key-value pairs for the following credentials: 
        {
            "fsid": "Valid Foursquare client Id",  
            "fssecret" : "Valid Foursquare client secret",  
            "censuskey" : "Valid US Census API Key"
        }
    """ 
    
    def __init__(self, address, credentials):
        """Initializes class object parameters."""
        pd.set_option('display.precision', 2)
        self.ADDRESS = str(address)
        self.CREDENTIALS = credentials
        try:
            self.LOCATION_DATA = VipDt.getCensusGeo(self)
            self.CENSUS_DATA = VipDt.getTractValues(self)
            self.LOCATION_DATA['TRACT'] = VipDt.getRadius(self)
        except:
            self.LOCATION_DATA = VipDt.getGeopyGeo(self)
            self.LOCATION_DATA['TRACT'] = {'RADIUS': 4250}
        self.FS_JSON = {
            'VENUES' : None,
            'MENUS' : None,
        }
        self.FS_SUMMARIES = {
            'VENUES' : pd.DataFrame(data={'test venues 1': [1, 2], 
                                          'test venues 2': [3, 4]}),
            'MENUS' : pd.DataFrame(data={'test menus 1': [5, 6], 
                                         'test menus 2': [7, 8]}),
            'STATS' : pd.DataFrame(data={'test stats 1': [9, 10], 
                                              'test stats 2': [11, 12]}),
            'MAP' : None
        }
        self.OUTPUT_LABELS = {
            'pickleLabel' : ("{}.pickle").format(self.ADDRESS),
            'jsonLabel' : ("{}.json").format(self.ADDRESS),
            'xlLabel' : ("{}.xlsx").format(self.ADDRESS),
            'foliumLabel' : ("{}.html").format(self.ADDRESS)
        }
    

    @staticmethod
    def getFileTokens(filename='certificate'):
        """A simple method for returning a dictionary of credentials 
        from a local text file.
        
        Parameters
        ----------
        filename: str
         the name of the file where key values are stored
        """
        # WOULD SWITCH THIS ALL TO CSV FORMAT INSTEAD
        credsfname = filename
        path = Path.cwd() / credsfname
        with path.open() as f:
            # Adding then removing '/n' chars per line for each key except the last.
            fsid = f.readline(50)  
            fssecret = f.readline(50)
            censuskey = f.readline(42)
        f.close()
        return {"fsid": fsid[:-1], "fssecret": fssecret[:-1], 'censuskey': censuskey}
    
    def getGeopyGeo(self, agent="foursquare app"):
        """Returns a dict of geolocation data for the 'target address'."""
        geolocator = Nominatim(user_agent=agent)
        address = str(self.ADDRESS)
        location = geolocator.geocode(address, addressdetails=True)
        ll = ("{},{}").format(str(location.latitude), 
                              str(location.longitude))
        return geolocator.geocode(ll, addressdetails=True)    
        
    def getCensusGeo(self,
                     options={
                         'benchmark':"Public_AR_Census2010",
                         'vintage':"Census2010_Census2010",
                         'layers':"08", 
                         'format':"json"}):
        """
        Returns geo data from the US Census Bureau for a given address.

        Parameters
        ----------
        options: dict
         contents include base parameters for accessing the US CENSUS BUREAU API
         at an endpoint hard coded into the method for security purposes.
        """
        _address = str(self.ADDRESS)
        _benchmark = str(options['benchmark'])
        _vintage = str(options['vintage'])
        _layers = str(options['layers'])
        _format = str(options['format'])
        _key = self.CREDENTIALS['censuskey']
        base_url = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?"
        params = ("address={}&benchmark={}&vintage={}&layers={}&format={}&key={}").format(
            _address,_benchmark,_vintage,_layers,_format,_key)
        api_url = ("{}{}").format(base_url, params)
        response = requests.get(api_url)
        json = response.json()
        return {"json": json, "status": str(response.status_code)}
    
    def getTractValues(self):
        "Returns US Census data."
        json = self.LOCATION_DATA['json']
        tract_id = json['result']['addressMatches'][0]['geographies']['Census Tracts'][0]['TRACT']
        county_id = json['result']['addressMatches'][0]['geographies']['Census Tracts'][0]['COUNTY']
        state_id = json['result']['addressMatches'][0]['geographies']['Census Tracts'][0]['STATE']
        land_area = json['result']['addressMatches'][0]['geographies']['Census Tracts'][0]['AREALAND']
        population = json['result']['addressMatches'][0]['geographies']['Census Tracts'][0]['POP100']
        census_vals = {
            "tract_id": tract_id, "county_id": county_id, 
            "state_id": state_id, "land_area": land_area, 
            "tract_pop": population
            }
        print("Census data found...")
        return census_vals

    def getRadius(self):
        """Returns demographic data for a given census tract."""
        api_key = self.CREDENTIALS['censuskey']
        tract_data = self.CENSUS_DATA
        area= float(tract_data['land_area'])
        geo = censusdata.censusgeo(
            [('state', str(tract_data['state_id'])),
             ('county', str(tract_data['county_id'])),
             ('tract', str(tract_data['tract_id']))]
        )
        ## ATTN! BELOW ARE CENSUS TABLE CODES WITH CORRESPONDING TITLES.
        data = censusdata.download(
            'acs5', 2015, geo,
                [
                    'B19001_001E',  # Total!!Respondents
                    'B19001_002E',  # Total!!Less than $10,000
                    'B19001_003E',  # Total!!$10,000 to $14,999
                    'B19001_004E',  # Total!!$15,000 to $19,999
                    'B19001_005E',  # Total!!$20,000 to $24,999
                    'B19001_006E',  # Total!!$25,000 to $29,999
                    'B19001_007E',  # Total!!$30,000 to $34,999
                    'B19001_008E',  # Total!!$35,000 to $39,999
                    'B19001_009E',  # Total!!$40,000 to $44,999
                    'B19001_010E',  # Total!!$45,000 to $49,999
                    'B19001_011E',  # Total!!$50,000 to $59,999
                    'B19001_012E',  # Total!!$60,000 to $74,999
                    'B19001_013E',  # Total!!$75,000 to $99,999
                    'B19001_014E',  # Total!!$100,000 to $124,999
                    'B19001_015E',  # Total!!$125,000 to $149,999
                    'B19001_016E',  # Total!!$150,000 to $199,999
                    'B19001_017E'   # Total!!$200,000 or more
                ], key=api_key)
        ## ATTN! BELOW ARE TABULATION VALUES FOR TARGET CENSUS TRACT.
        TRACT_DATA = {
                "tractid": self.CENSUS_DATA['tract_id'], 
                "countyid": self.CENSUS_DATA['county_id'], 
                "stateid": self.CENSUS_DATA['state_id'], 
                "landarea": self.CENSUS_DATA['land_area'], 
                "tractpop100": self.CENSUS_DATA['tract_pop'],
                "Total respondents": data.B19001_001E,
                "Income < $10000" : 10000 * data.B19001_002E,
                "Income ~ $12500" : 12500 * data.B19001_003E,
                "Income ~ $17500" : 17500 * data.B19001_004E,
                "Income ~ $22500" : 22500 * data.B19001_005E,
                "Income ~ $27500" : 27500 * data.B19001_006E,
                "Income ~ $32500" : 32500 * data.B19001_007E,
                "Income ~ $37500" : 37500 * data.B19001_008E,
                "Income ~ $42500" : 42500 * data.B19001_009E,
                "Income ~ $47500" : 47500 * data.B19001_010E,
                "Income ~ $55000" : 55000 * data.B19001_011E,
                "Income ~ $67500" : 675000 * data.B19001_012E,
                "Income ~ $87500" : 87500 * data.B19001_013E,
                "Income ~ $112500": 112500 * data.B19001_014E,
                "Income ~ $137500": 137500 * data.B19001_015E,
                "Income ~ $175000": 175000 * data.B19001_016E,
                "Income > $200000": 200000 * data.B19001_017E
                }
        ## ATTN! BELOW ARE CALCULATIONS FOR AVG INCOME PER TRACT 'POP100' 
        AVG_INCOME = float((
            (10000 * data.B19001_002E) + (12500 * data.B19001_003E) 
            + (17500 * data.B19001_004E) + (22500 * data.B19001_005E) 
            + (27500 * data.B19001_006E) + (32500 * data.B19001_007E) 
            + (37500 * data.B19001_008E) + (42500 * data.B19001_009E) 
            + (47500 * data.B19001_010E) + (55000 * data.B19001_011E) 
            + (67500 * data.B19001_012E) + (87500 * data.B19001_013E)
            + (112500 * data.B19001_014E) + (137500 * data.B19001_015E) 
            + (175000 * data.B19001_016E) + (200000 * data.B19001_017E)) 
            / TRACT_DATA['tractpop100'])
        ## ATTN! BELOW ARE CALCULATIONS FOR THE DYNAMIC SEARCH RADIUS
        pop = TRACT_DATA['tractpop100']
        fsRadius = (((area/pop)/ 6.28)**3
                    +(AVG_INCOME/pop)**3)**(1/2)+1000.00
        if fsRadius > 50000.00: 
            radius = 50000.00
        elif fsRadius < 1000.00: 
            radius = 1000.00
        else: 
            radius = fsRadius
        TRACT_DATA["Avg income"] = AVG_INCOME
        TRACT_DATA["RADIUS"] = radius
        print("Search radius:", radius)
        return TRACT_DATA
    
    def getVenues(self, latlng=None, query="", radius=None,  
                  intent="browse", limit=50, 
                  categories=['4d4b7105d754a06376d81259', 
                              '4d4b7105d754a06374d81259']):
        """
        Method for returning raw venue data for location 'ADDRESS'.

        Parameters
        ----------
        latlng: str
         latitude,longitude as comma-separated string values
        query: str
         a value to filter results
        radius: float, int
         a search radius in meters
        intent: str
         "browse" by default. 
        limit: int
         the limit of responses, 1-50 max
        categories: list
         a list of category string values to filter or expand results

        See Foursquare API docs for more details.
        """
        client = foursquare.Foursquare(client_id = self.CREDENTIALS['fsid'], 
                                       client_secret = self.CREDENTIALS['fssecret'])
        if radius is None:
            radius = self.LOCATION_DATA['TRACT']['RADIUS']
        if latlng is None:
            latlng = self.LOCATION_DATA['TRACT']['RADIUS']
        coords = tuple(self.LOCATION_DATA['json']['result']
                       ['addressMatches'][0]['coordinates'].values())
        ll = ("{},{}").format(coords[1],coords[0])
        responses ={}
        for category in categories:
            params = {
                'query': str(query), 
                'll': ll,
                'categoryId': category, 
                'radius': radius,
                'intent': str(intent), 
                'limit': limit
            }
            responses[category] = client.venues.search(params)
        self.FS_JSON['VENUES'] = responses
        print("Venue query operation complete!")
        return responses
    
    def getMenus(self,venues=None):
        """
        A method for returning raw menu data.

        Parameters
        ----------
        venues: list
         a list of venue id numbers to query for menu data
        """
        if venues is None:
            venues_dict = self.FS_JSON['VENUES']
        client = foursquare.Foursquare(client_id = self.CREDENTIALS['fsid'], 
                                       client_secret = self.CREDENTIALS['fssecret'])
        unique_ids = []
        menus = {}
        try:
            for key in venues_dict:
                print("Querying menu data for key:", key)
                for venue in venues_dict[key]['venues']:
                    venue_name = venue['name']
                    venue_id = venue['id']
                    if (venue_id in unique_ids):
                        pass
                    else:
                        unique_ids += [venue_id]
                        response = client.venues.menu(venue_id)
                        menus[venue_name] = response
        except:
            traceback.print_exc()
        self.FS_JSON['MENUS'] = menus
        print("Menu query operation complete!")
        return menus

    def setMenusDf(self, records=None, drop_na=False, iter_limit=None):
        """
        A method for extracting a dataframe from 'MENUS' json.

        Parameters
        ----------
        records: list
         a list of menu query responses
        drop_na: bool
         indicates whether to drop NoneTypes from dataframe, False by default 
        iter_limit: int
         the number of maximum observations per dataframe
        """
        if records is None:
            records = self.FS_JSON['MENUS']
        bulk_items = []
        for key in records:
            if records[key]['menu']['menus']['count'] > 0:
                menus = records[key]['menu']['menus']['items']
                for menu in menus:
                    menu_name = menu['name']
                    if menu['entries']['count'] > 0:
                        sections = menu['entries']['items']
                        for section in sections:
                            section_name = section['name']
                            if section['entries']['count'] > 0:
                                items = section['entries']['items']
                                for item in items:
                                    try:
                                        item_name = item['name']
                                    except KeyError:
                                        item_name = None
                                    try:
                                        item_desc = item['description']
                                    except KeyError:
                                        item_desc = None
                                    try:
                                        item_price = float(item['price'])
                                    except (KeyError, TypeError):
                                        item_price = None
                                    bulk_items += [{
                                        'venue_name': key,
                                        'menu_name': menu_name,
                                        'section_name': section_name,
                                        'item_name': item_name,
                                        'item_desc': item_desc,
                                        'item_price' : item_price
                                    }]
                            else:
                                # print("NO ITEMS IN SECTION", section_name)
                                pass
                    else:
                        # print("NO SECTIONS IN MENU:", menu_name)
                        pass
            else:
                # print("NO MENUS IN VENUE:", key)
                pass
        try:
            df = pd.DataFrame.from_records(bulk_items, index=None, exclude=None,
                                           coerce_float=True, nrows=iter_limit,
                                           columns=['venue_name',
                                                    'menu_name', 
                                                    'section_name', 
                                                    'item_name', 
                                                    'item_desc', 
                                                    'item_price'])
            if drop_na==True:
                df.dropna(inplace=True)
            self.FS_SUMMARIES['MENUS'] = df
            return df
        except TypeError:
            traceback.print_exc
            print("Error! Failed to create dataframe.")
            pass

    def getVenuesMap(self, save_map=True):
        """
        A method for creating a Folium map from 'VENUES' json

        Parameters
        ----------
        save_map: bool
         indicates whether to save a venue location map as html
        """
        venue_data = self.FS_JSON['VENUES']
        search_address = self.LOCATION_DATA['json']['result']['addressMatches'][0]['matchedAddress']
        search_lat = self.LOCATION_DATA['json']['result']['addressMatches'][0]['coordinates']['y']
        search_lng = self.LOCATION_DATA['json']['result']['addressMatches'][0]['coordinates']['x']
        search_coords = (search_lat,search_lng)
        m = folium.Map(
            name="Venue Locations", location=search_coords, zoom_start=12, control_scale=True)
        folium.CircleMarker(
            search_coords, popup = search_address, tooltip = search_address).add_to(m)
        for category in venue_data:
            venue_category = category
            for venue in venue_data[category]['venues']:
                venue_name = venue['name']
                venue_type = venue['categories'][0]['name']
                venue_lat = venue['location']['lat']
                venue_lng = venue['location']['lng']
                venue_coords = (venue_lat,venue_lng)
                ## 'Nightlife' ID: "4d4b7105d754a06376d81259"
                if venue_category=="4d4b7105d754a06376d81259":  
                    folium.Marker(
                        venue_coords, popup = venue_type, tooltip = venue_name,
                        icon = folium.Icon(
                            icon= 'glyphicon-glass', color = 'blue')
                        ).add_to(m)
                ## 'Food' ID:'4d4b7105d754a06374d81259'
                elif venue_category=='4d4b7105d754a06374d81259':  
                    folium.Marker(
                        venue_coords, popup = venue_type, tooltip = venue_name,
                        icon = folium.Icon(
                            icon='glyphicon-cutlery', color = 'red')
                        ).add_to(m)
                else:
                    folium.Marker(
                        venue_coords, popup = venue_type, tooltip = venue_name,
                        icon = folium.Icon(
                            icon='glyphicon-map-marker', color = 'orange')
                        ).add_to(m)
        self.FS_SUMMARIES['MAP'] = m
        if save_map == True:
            m.save(self.OUTPUT_LABELS['foliumLabel'])
        return m

    def setVenuesDf(self):
        """A method for extracting a dataframe of local venues from 'VENUES' json."""
        json = self.FS_JSON['VENUES']
        venue_list = []
        for category in json:
            category_idn = category
            venues = json[category]['venues']
            for venue in venues:
                venue_name = venue['name']
                try:
                    venue_address = venue['location']['address']
                except:
                    venue_address = None
                try:
                    venue_lat = venue['location']['lat']
                except:
                    venue_lat = None
                try:
                    venue_lng = venue['location']['lng']
                except:
                    venue_lng = None
                venue_list += [{
                    "venue_name": venue_name,
                    "category_idn": category_idn,
                    "venue_address": venue_address,
                    "venue_lat": venue_lat,
                    "venue_lng": venue_lng
                }]
        df = pd.DataFrame.from_records(
            venue_list, index=None, exclude=None, coerce_float=False, 
            columns=['venue_name','category_idn', 'venue_address', 'venue_lat', 'venue_lng'])
        self.FS_SUMMARIES['VENUES'] = df
        return df
    
    def getMenuStats(self, menus=None, confidence=0.99):
        """
        Returns a dictionary of dataframes with descriptive 'price' analyses.

        Parameters
        ----------
        menus: list
         a list of menu query json responses
        confidence: float
         a confidence decimal value between >0 and <1 for the "bayes_mvs" bootstrap method
        """
        menu_df = self.FS_SUMMARIES['MENUS']
        if menus is not None:
            menu_df = menus
        menu_data = menu_df[
            ['venue_name', 'menu_name', 'section_name', 'item_name', 'item_desc', 
            'item_price']
            ]
        # menu_data['item_price'] = menu_data['item_price'].astype('float64')
        menu_data = menu_data.dropna()
        menu_desc = menu_data.groupby(['menu_name']).describe()
        explore_menus = menu_data.groupby(
            ['venue_name', 'menu_name', 'section_name']).describe()
        items = menu_data['item_price']
        bayes_stats = scipy.stats.bayes_mvs(items, alpha=confidence)
        menuStats = {"menu_items": menu_data, "menu_desc": menu_desc, 
                    "explore_menus": explore_menus, "bayes_mvs": bayes_stats}
        self.FS_SUMMARIES['STATS'] = menuStats
        return menuStats

    def setPickle(self, pickle_name='instance.pickle'):
        """
        Method for serializing the current instance. LESS SECURE THAN JSON.
        
        Parameters
        ----------
        pickle_name: str
         a file name for the pickled instance
        """
        try:
            # pickleName = self.pickleName
            self.FS_SUMMARIES['MAP'] = None  # Cuz cannot serialize folium map objects.
            with open(pickle_name, 'wb') as f:
                pickle.dump(self, f)
            f.close()
            print(pickle_name, "serialized!")
            return pickle_name
        except:
            print("ERROR!", pickle_name, "NOT serialized!")
            traceback.print_exc()
            return

    def setJson(self, jsonName = 'FS_JSON.json'):
        """
        A method for serializing data from the current instance.
        
        Parameters
        ----------
        jsonName: str
         a file name for storing json objects
        """
        data = self.FS_JSON
        with open(jsonName, "w") as f:
            json.dump(data, f)
            f.close()
        print(jsonName, "JSON file created!")    
        return data   

    @staticmethod
    def getPickle(file_name='instance.pickle'):
        """
        Method for deserializing an instance. LESS SECURE THAN JSON.
        
        Parameters
        ----------
        file_name: str
         a file name for retrieving pickled objects. 'instance.pickle' by default.
        """
        pickleName = file_name
        try:
            with open(pickleName, 'rb') as f:
                data = pickle.load(f)
                f.close()
            print(pickleName, "found!")
            return data
        except:
            print("ERROR!", pickleName, "file NOT found!")
            traceback.print_exc()
            return

    def getJson(self, file_name='FS_JSON.json'):
        """
        A method for reconstituting previously serialized JSON data. 'FS_JSON.json' by default.

        Parameters
        ----------
        file_name: str
         a file name for retrieving json objects.
        """
        jsonName = file_name
        with open(jsonName, "r") as f:
            data = f.read()
            f.close()
            print(jsonName, "found!")
        value = json.load(data)
        venues = pd.read_json(value["VENUES"])
        menus = pd.read_json(value["MENUS"])
        payload = {
            "VENUES": venues, "MENUS": menus
            }
        self.FS_JSON=payload
        return payload

    def stats2Excel(self, sheets=None):
        """
        A method for exporting instance data as a spreadsheet.
        
        Parameters
        ----------
        sheets: dict
         a dict of dataframe objects from 'FS_SUMMARIES['STATS']'.
        """
        if sheets is None:
            sheets = self.FS_SUMMARIES['STATS']
        sheet_file_name = self.OUTPUT_LABELS['xlLabel']
        with pd.ExcelWriter(sheet_file_name) as writer:
            for item in sheets:
                if isinstance(sheets[item], pd.DataFrame):
                    df = sheets[item]
                    df.to_excel(writer, sheet_name=item)
                else :
                    try:
                        df = pd.DataFrame(data=sheets[item])
                        df.to_excel(writer, sheet_name=item)
                    except:
                        print("Error! 'item' skipped.")
                        pass
        writer.close()
        print("Export complete!")
        return

    @staticmethod
    def start(address=None, credentials=None):
        """
        A method for automatically populating an instance with data.
        
        Parameters
        ----------
        address: str
          A real address for a particular location
        credentials: dict
          Key-value pairs for the following credentials: 
        {
            "fsid": "Valid Foursquare client Id",  
            "fssecret" : "Valid Foursquare client secret",  
            "censuskey" : "Valid US Census API Key"
        }
        """
        if address is None:
            address = input("Enter address here:") 
        if credentials is None:
            credentials = VipDt.getFileTokens()
        try:
            ## INITIALIZATION
            client = VipDt(address, credentials)
            try:
                ## VENUES
                client.getVenues()
                client.setVenuesDf()
                client.getVenuesMap()
                try:
                    ## MENUS
                    client.getMenus()
                    client.setMenusDf()
                    client.getMenuStats()
                    # client.setPickle()
                    # try:
                    #     ## REPORTS
                    #     client.stats2Excel()
                    # except:
                    #     print('Report failed!')
                    #     pass
                    print("Procedure complete!")
                    # return #client.FS_SUMMARIES
                except:
                    print('Menus failed!')
                    pass
            except:
                print('Venues failed!')
                pass
        except:
            print('Initialization failed! Procedure aborted.')
            pass

## EXAMPLES OF ACCESSING POST-QUERY DATA
# instance.FS_SUMMARIES['MENUS'].hist(bins=100)
# a1.FS_SUMMARIES['MENUS'].describe()
# a2.FS_SUMMARIES['STATS']['menu_desc']
# a3.FS_SUMMARIES['VENUES']