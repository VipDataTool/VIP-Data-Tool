"""
MIT License  

Copyright (c) 2019 VipDataTool

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
import pandas as pd 
import scipy.stats
import requests
import folium
import numpy as np

pd.set_option('display.precision', 2)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 50)
print("Dependencies imported.")


class VipDt:
    """
    Description
    -----------
        A collection of methods for returning venue data for 
        a given US address from the Foursquare Places API.

    Parameters
    ----------
    address: str
        A real address for a given location.
    credentials: dict
        Key-value pairs for the following credentials: 
            {"fsid": "Valid Foursquare Client Id",
            "fssecret" : "Valid Foursquare Client Secret",
            "censuskey" : "Valid US Census API Key"}
    
    How To Use
    ----------
        1) import VipDt as vd       # IMPORTS CLASS MODULE
        2) dt = vd(address, creds)  # INSTANTIATES CLASS OBJECT
        3) dt.getVenues()           # QUERIES LOCATION FOR VENUES
        4) dt.getMenus()            # QUERIES VENUES FOR MENUS
        5) dt.getVenuesMap()        # CREATES VENUE LOCATION MAP
        6) dt.setVenuesDf()         # CREATES DATAFRAME FROM VENUES
        7) dt.setMenusDf()          # CREATES DATAFRAME FROM MENUS
        8) dt.getMenuStats()        # CREATES STATS PKG FROM DATA
    """

    def __init__(self, address, credentials):
        """
        Description
        -----------
            Initializes class object parameters.
        """
        self.__version__ = '1.0.1'
        self.ADDRESS = str(address)  # STRING
        self.CREDENTIALS = credentials  # DICTIONARY
        self.LOCATION_DATA = VipDt.getCensusGeo(self)  # DICTIONARY
        self.TRACT_DATA = VipDt.getTractValues(self)  # DICTIONARY
        self.FS_JSON = {'VENUES':None, 'MENUS':None}
        self.FS_SUMMARIES = {
            'VENUES':None, 'MENUS':None, 'STATS':None, 'MAP':None
            }
        self.OUTPUT_LABELS = {
            'pickleLabel' : ("{}.pickle").format(self.ADDRESS),
            'jsonLabel' : ("{}.json").format(self.ADDRESS),
            'xlLabel' : ("{}.xlsx").format(self.ADDRESS),
            'foliumLabel' : ("{}.html").format(self.ADDRESS)
            }
        self.VENUE_CATEGORIES = {
            "COLOR_CODES": [
                'lightred', 'lightblue', 'lightgreen', 'cadetblue', 
                'red', 'blue', 'green', 'orange', 'purple', 'pink', 
                'darkred', 'darkblue', 'darkgreen', 'darkpurple', 
                'gray', 'lightgray', 'black', 'white', 'beige'],
            "CATEGORIES":{
                "4d4b7104d754a06370d81259": [
                    "Arts & Entertainment", 
                    "glyphicon glyphicon-music",
                    "darkblue"],
                "4d4b7105d754a06372d81259": [
                    "College & University", 
                    "glyphicon glyphicon-pencil",
                    "orange"],
                "4d4b7105d754a06373d81259": [
                    "Event", 
                    "glyphicon glyphicon-calendar",
                    "purple"],
                "4d4b7105d754a06374d81259": [
                    "Food", 
                    "glyphicon glyphicon-cutlery",
                    "red"],
                "4d4b7105d754a06376d81259": [
                    "Nightlife Spot", 
                    "glyphicon glyphicon-glass",
                    "blue"],
                "4d4b7105d754a06377d81259": [
                    "Outdoors & Recreation", 
                    "glyphicon glyphicon-tree-conifer",
                    "green"],
                "4d4b7105d754a06375d81259": [
                    "Professional & Other Places", 
                    "glyphicon glyphicon-envelope",
                    "lightgray"],
                "4e67e38e036454776db1fb3a": [
                    "Residence", 
                    "glyphicon glyphicon-home",
                    "gray"],
                "4d4b7105d754a06378d81259": [
                    "Shop & Service", 
                    "glyphicon glyphicon-shopping-cart",
                    "pink"],
                "4d4b7105d754a06379d81259": [
                    "Travel & Transport", 
                    "glyphicon glyphicon-plane",
                    "cadetblue"]
                }
            }
        print("Version:", self.__version__," object initialized!")

            
    @staticmethod
    def getJsonTokens(file_name="credentials.json"):
        """
        Description
        -----------
            A method for reconstituting previously serialized JSON data.

        Parameters
        ----------
        file_name: str
            A json file name for retrieving credentials.
        """
        jsonName = file_name
        with open(jsonName,"r") as f:
            data = json.load(f)
            f.close()
            print(jsonName, "found!")
        return data

    def getCensusGeo(self, options={
                            'benchmark':"Public_AR_Census2010",
                            'vintage':"Census2010_Census2010",
                            'layers':"08"}):
        """
        Description
        -----------
            Returns geo data from the US Census Bureau for a given address.

        Parameters
        ----------
        options: dict
            Contents include base parameters for accessing the US CENSUS BUREAU API
            at an endpoint hard coded into the method for security purposes.
        """
        _address = str(self.ADDRESS)
        _benchmark = str(options['benchmark'])
        _vintage = str(options['vintage'])
        _layers = str(options['layers'])
        _format = "json"
        _key = self.CREDENTIALS['censuskey']
        base_url = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?"
        params = ("address={}&benchmark={}&vintage={}&layers={}&format={}&key={}").format(
            _address,_benchmark,_vintage,_layers,_format,_key)
        api_url = ("{}{}").format(base_url, params)
        response = requests.get(api_url)
        json = response.json()
        return {"json": json, "status": str(response.status_code)}
    
    def getTractValues(self):
        """
        Description
        -----------
            Returns demographic data for a given US Census tract.
        """
        json = self.LOCATION_DATA['json']
        tract_id = json['result']['addressMatches'][0]\
            ['geographies']['Census Tracts'][0]['TRACT']
        county_id = json['result']['addressMatches'][0]\
            ['geographies']['Census Tracts'][0]['COUNTY']
        state_id = json['result']['addressMatches'][0]\
            ['geographies']['Census Tracts'][0]['STATE']
        land_area = json['result']['addressMatches'][0]\
            ['geographies']['Census Tracts'][0]['AREALAND']
        population = json['result']['addressMatches'][0]\
            ['geographies']['Census Tracts'][0]['POP100']
        census_vals = {
            "tract_id": tract_id, "county_id": county_id, 
            "state_id": state_id, "land_area": land_area, 
            "tract_pop": population
            }
        print("Census data found...")
        api_key = self.CREDENTIALS['censuskey']
        area= float(census_vals['land_area'])
        geo = censusdata.censusgeo(
            [('state', str(census_vals['state_id'])),
             ('county', str(census_vals['county_id'])),
             ('tract', str(census_vals['tract_id']))]
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
                "tractid": census_vals['tract_id'], 
                "countyid": census_vals['county_id'], 
                "stateid": census_vals['state_id'], 
                "landarea": census_vals['land_area'], 
                "tractpop100": census_vals['tract_pop'],
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
                "Income ~ $67500" : 67500 * data.B19001_012E,
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
        ## ATTN! BELOW ARE CALCULATIONS FOR DYNAMIC SEARCH RADIUS
        pop = TRACT_DATA['tractpop100']
        fsRadius = (((area/pop)/ 3.14)**3
                    +(AVG_INCOME/pop)**3)**(1/2.5)+1000.00
        if fsRadius > 50000.00: 
            radius = 50000.00
        elif fsRadius < 1000.00: 
            radius = 1000.00
        else: 
            radius = fsRadius
        TRACT_DATA["AVG_INCOME"] = AVG_INCOME
        TRACT_DATA["RADIUS"] = radius
        print("Search radius:", radius)
        return TRACT_DATA
    
    def getVenues(self, latlng=None, query="", radius=None,  
                  intent="browse", limit=50, 
                  categories=None):                
        """
        Description
        -----------
            Method for returning raw venue data for 'ADDRESS'.

        Parameters
        ----------
        latlng: str
            Latitude, longitude as a comma-separated string values.
        query: str
            A value to filter results.
        radius: float, int
            A search radius in meters.
        intent: str
            Set to "browse" by default. 
        limit: int
            The max limit of responses, 1-50 max.
        categories: str, list
            Accepts a 'category id' as a string value,
            or 'all' to search each key in VENUE_CATEGORIES,
            or a list of specific 'category id' numbers to search.

        See Foursquare API docs for more details on query parameters.
        """
        if radius is None:
            radius = self.TRACT_DATA['RADIUS']
        if isinstance(latlng,str):
            ll = latlng
        else:
            coords = tuple(self.LOCATION_DATA['json']['result']\
                ['addressMatches'][0]['coordinates'].values())
            ll = ("{},{}").format(coords[1],coords[0])
        if categories is None:
            ## 'Nightlife' CATEGORY ID  : "4d4b7105d754a06376d81259"
            ## 'Food' CATEGORY ID       : '4d4b7105d754a06374d81259' 
            categories = ['4d4b7105d754a06376d81259', '4d4b7105d754a06374d81259']
        elif isinstance(categories,str):
            categories = [categories]
        elif isinstance(categories,str) and categories=="all":
            categories = list(self.VENUE_CATEGORIES['CATEGORIES'].keys())
        else:
            pass
        client = foursquare.Foursquare(
            client_id = self.CREDENTIALS['fsid'], 
            client_secret = self.CREDENTIALS['fssecret'])
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
        return #responses

    def setVenuesDf(self):
        """
        Description
        -----------
            A method for extracting a dataframe of from 'VENUES' json.
        """
        json = self.FS_JSON['VENUES']
        venue_list = []
        for category in json:
            category_idn = category
            venues = json[category]['venues']
            for venue in venues:
                try:
                    venue_name = venue['name']
                except KeyError:
                    venue_name = None
                try:
                    venue_id = venue['id']
                except KeyError:
                    venue_id = None
                try:
                    venue_address = venue['location']['address']
                except KeyError:
                    venue_address = None
                try:
                    venue_lat = venue['location']['lat']
                except KeyError:
                    venue_lat = None
                try:
                    venue_lng = venue['location']['lng']
                except KeyError:
                    venue_lng = None
                try:
                    venue_referral_id = venue["referralId"]
                except KeyError:
                    venue_referral_id = None
                try:
                    delivery_provider = venue['delivery']['provider']['name']
                except KeyError:
                    delivery_provider = None
                try:
                    delivery_url = venue['delivery']['url']
                except KeyError:
                    delivery_url = None
                try:
                    vid = str(venue_id)
                    ## CODE FOR FOURSQUARE REFERRAL WITHOUT CLIENT_ID:
                    string_url = ("https://foursquare.com/v/{}").format(vid)

                    ## CODE FOR FOURSQUARE REFERRAL WITH CLIENT_ID:
                    # cid = self.CREDENTIALS['fsid']
                    # string_url = ("https://foursquare.com/v/{}&ref={}").format(vid,cid)
                except:
                    string_url = None
                venue_list += [{
                    "venue_name": venue_name,
                    "venue_id": venue_id,
                    "category_idn": category_idn,
                    "venue_address": venue_address,
                    "venue_lat": venue_lat,
                    "venue_lng": venue_lng,
                    "venue_referral_id": venue_referral_id,
                    "delivery_provider": delivery_provider,
                    "delivery_url": delivery_url,
                    "attribution_link": string_url
                }]
        df = pd.DataFrame.from_records(
            venue_list, index=None, exclude=None, coerce_float=False, 
            columns=['venue_name',"venue_id",'category_idn', 'venue_address', \
                'venue_lat', 'venue_lng', "venue_referral_id", "delivery_provider", 
                "delivery_url"])
        self.FS_SUMMARIES['VENUES'] = df
        return df

    def getVenuesMap(self, save_map=True):
        """
        Description
        -----------
            A method for creating a Folium map from 'VENUES' json.

        Parameters
        ----------
        save_map: bool
            Indicates whether to output the venue location map as an html.
        """
        venue_data = self.FS_JSON['VENUES']
        search_address = self.LOCATION_DATA['json']['result']\
            ['addressMatches'][0]['matchedAddress']
        search_lat = self.LOCATION_DATA['json']['result']\
            ['addressMatches'][0]['coordinates']['y']
        search_lng = self.LOCATION_DATA['json']['result']\
            ['addressMatches'][0]['coordinates']['x']
        search_coords = (search_lat,search_lng)
        m = folium.Map(
            name="Venue Locations", location=search_coords, 
            zoom_start=13, control_scale=True)
        folium.CircleMarker(
            search_coords, popup = search_address, 
            tooltip = search_address).add_to(m)
        for category in venue_data:
            for venue in venue_data[category]['venues']:
                venue_name = venue['name']
                venue_id = venue['id']
                venue_type = venue['categories'][0]['name']
                venue_lat = venue['location']['lat']
                venue_lng = venue['location']['lng']
                try:
                    venue_icon = self.VENUE_CATEGORIES['CATEGORIES'][category][1]
                    venue_icon_color = self.VENUE_CATEGORIES['CATEGORIES'][category][2]
                except KeyError:
                    venue_icon = "glyphicon glyphicon-search"
                    venue_icon_color = 'lightblue'
                attribution_url = (
                    "<a href=https://foursquare.com/v/{}>{}</a>").format(
                        venue_id, 
                        venue_type)
                venue_coords = (venue_lat, venue_lng)
                folium.Marker(
                    venue_coords, 
                    popup = attribution_url, 
                    tooltip = venue_name,
                    icon = folium.Icon(
                        icon= venue_icon,
                        color= venue_icon_color)
                    ).add_to(m)
        self.FS_SUMMARIES['MAP'] = m
        if save_map == True:
            m.save(self.OUTPUT_LABELS['foliumLabel'])
        return m

    def getMenus(self,venues=None):
        """
        Description
        -----------
            A method for returning venue menu query response data.

        Parameters
        ----------
        venues: list
            A list of venue id numbers to query for menu data.
        """
        if venues is None:
            venues_dict = self.FS_JSON['VENUES']
        client = foursquare.Foursquare(
            client_id = self.CREDENTIALS['fsid'], 
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
        return #menus

    def setMenusDf(self, records=None, drop_na=False, iter_limit=None, drop_menus_with=[]):
        """
        Description
        -----------
            A method for extracting a dataframe from 'MENUS' json.

        Parameters
        ----------
        records: list
            A list of menu query responses.
        drop_na: bool
            Drops 'NoneTypes' from dataframe. 'False' by default.   
        iter_limit: int
            Maximum number of observations per dataframe. 'None' by default.
        """
        if records is None:
            records = self.FS_JSON['MENUS']
        bulk_items = []
        for key in records:
            if records[key]['menu']['menus']['count'] > 0:
                menus = records[key]['menu']['menus']['items']
                for menu in menus:
                    if menu['entries']['count'] > 0:
                        sections = menu['entries']['items']
                        for section in sections:
                            if section['entries']['count'] > 0:
                                items = section['entries']['items']
                                for item in items:
                                    try:
                                        menu_name = menu['name']
                                    except KeyError:
                                        menu_name = "No menu title"
                                    try:
                                        section_name = section['name']
                                    except KeyError:
                                        section_name = "No section title"
                                    try:
                                        item_name = item['name']
                                    except KeyError:
                                        item_name = "No item name"
                                    try:
                                        item_desc = item['description']
                                    except KeyError:
                                        item_desc = "No item description"
                                    try:
                                        item_price = float(item['price'])
                                    except (KeyError, ValueError):
                                        item_price = None
                                    try:
                                        attribution_link = records[key]['menu']\
                                            ['provider']['attributionLink']
                                    except KeyError:
                                        attribution_link = None
                                    bulk_items += [{
                                        'venue_name': key,
                                        'menu_name': menu_name,
                                        'section_name': section_name,
                                        'item_name': item_name,
                                        'item_desc': item_desc,
                                        'item_price' : item_price,
                                        'attribution': attribution_link
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
            df = pd.DataFrame.from_records(
                bulk_items, index=None, exclude=None, coerce_float=True, 
                nrows=iter_limit, columns=['venue_name', 'menu_name', 
                'section_name', 'item_name', 'item_desc', 'item_price', 
                'attribution'])
            if drop_na==True:
                df.dropna(inplace=True)
            if isinstance(drop_menus_with, list) and len(drop_menus_with)>0:
                filter_index_list = []
                for menu_name in df['menu_name'].iteritems():
                    menu_string = menu_name[1]
                    for string in drop_menus_with:
                        if str(string) in menu_string:
                            filter_index_list += [menu_name[0]]
                        else:
                            pass
                df.drop(filter_index_list, inplace=True)
            self.FS_SUMMARIES['MENUS'] = df
            return df
        except TypeError:
            traceback.print_exc
            print("Error! Failed to create dataframe.")
            pass

    def getMenuStats(self, menus=None, confidence=0.99):
        """
        Description
        -----------
            Returns a dictionary of dataframes with descriptive 'price' analyses.

        Parameters
        ----------
        menus: list
            A list of menu query json responses.
        confidence: float
            A confidence interval between 0 and 1 for 'bayes_mvs' method.
        """
        menu_df = self.FS_SUMMARIES['MENUS']
        if menus is not None:
            menu_df = menus
        menu_data = menu_df[['venue_name', 'menu_name', 'section_name', \
            'item_name', 'item_desc', 'item_price']]
        # menu_data['item_price'] = menu_data['item_price'].astype('float64')
        # menu_data['item_price'].astype('float64', inplace=True)
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

    def setJson(self):
        """
        Description
        -----------
            A method for serializing data from the current instance.
        
        Parameters
        ----------
        jsonName: str
            A file name for storing json objects.
        """
        jsonName = self.OUTPUT_LABELS['jsonLabel']
        data = self.FS_JSON
        with open(jsonName, "w") as f:
            json.dump(data, f)
            f.close()
        print(jsonName, "JSON file created!")    
        return data 

    def getJson(self, file_name):
        """
        Description
        -----------
            A method for reconstituting previously serialized JSON data.

        Parameters
        ----------
        file_name: str
            A file name for retrieving json objects.
        """
        jsonName = file_name
        with open(jsonName, "r") as f:
            data = f.read()
            f.close()
            print(jsonName, "found!")
        value = json.load(data)
        # location=
        venues = pd.read_json(value["VENUES"])
        menus = pd.read_json(value["MENUS"])
        payload = {"VENUES": venues, "MENUS": menus}
        self.FS_JSON=payload
        return payload

    def stats2Excel(self, sheets=None):
        """
        Description
        -----------
            A method for exporting instance data as a spreadsheet.
        
        Parameters
        ----------
        sheets: dict
            A dict of dataframe objects from 'FS_SUMMARIES['STATS']'.
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
        Description
        -----------
            A method for automatically populating an instance with data.
        
        Parameters
        ----------
        address: str
            A real address for a particular location.
        credentials: dict
            Key-value pairs for the following credentials: 
                {"fsid": "Valid Foursquare client Id",  
                "fssecret" : "Valid Foursquare client secret",  
                "censuskey" : "Valid US Census API Key"}
        """
        if address is None:
            address = input("Enter address here:") 
        if credentials is None:
            credentials = VipDt.getJsonTokens()
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
                    client.setPickle()
                    client.setJson()
                    print("Procedure complete!")
                except:
                    print('Menus failed! Procedure incomplete.')
                    pass
            except:
                print('Venues failed!')
                pass
        except:
            print('Initialization failed! Procedure aborted.')
            pass


"""
## EXAMPLES OF INTERACTING WITH THIS MODULE:
--------------------------------------------
## IMPORT CLASS MODULE
# import VipDt as vd

## CREATE CLASS OBJECT
# dt = vd(address, credentials)

## QUERY LOCATION FOR VENUES
# dt.getVenues()

## QUERY VENUES FOR MENUS
# dt.getMenus()

## EXAMINE QUERY RESULTS
# dt.getVenuesMap()
# dt.setVenuesDf()
# dt.setMenusDf()
# dt.getMenuStats()
"""