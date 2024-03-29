# VIP DATA TOOL

PURPOSE:  
I made this application to aggregate location-based venue data for restaurateurs interested in performing independent market research and location-based competitor analysis. 
  
DESCRIPTION:  
V.I.P. stands for "Venues in Places" referring to the Foursquare 'Places' API. A description of the endpoint can be found here: <https://developer.foursquare.com/docs/api>  
  
This module is essentially just a wrapper for the Python library referenced here: <https://developer.foursquare.com/docs/api/libraries>  
  
HOW IT WORKS:  
Start by creating an instance of the class object by passing two arguments:  
    1) A string value of an existing address i.e. "123 some st., sometown, somestate, somecountry"  
    2) A dictionary of credentials including the following key values:  
    - "fsid": "Valid Foursquare User Id",  
    - "fssecret" : "Valid Foursquare User Key",  
    - "censuskey" : "Valid US Census API Key"  

The resulting instance can then be treated as a client for querying venue information specific to the area defined by the aforementioned address and a radius dynamically calculated based upon available location demographic data. To query venue data, simply call the 'setter' and 'getter' methods provided to populate the object with data.  

A localized map can be generated from the venue data, as well as dataframes of the subsequent demographic, venue and menu data for further reference or analysis.  
  
Unprocessed query data can be serialized as a JSON file if necessary. Instances can be 'pickled', however any embedded Folium objects cannot.  
  
I included a simple static method titled 'getJsonTokens()' for retrieving one's credentials from a json document titled "certificate,json" located in the root directory of the script. This method is FAR from a secure method of storing one's user credentials, and is only intended to be used as a very short-term solution in a secure environment. Be sure to '.gitignore' this file if you intend to use this method as to avoid publishing your private API credentials on a public repository. For those looking to implement this library in a production environment, I highly recommend storing these credentials as environmental variables and refactoring the provided method as necessary using os.getenv(). Use at your own risk!!
  
USER DATA OBJECTS:  
VipData.JSON_DATA - Contains user-defined variables.
VipData.REPORTS - Contains derived data products.
  
USER METHODS:  
VipData.getVenues()* - Assembles a list of nearby venues approximate to a given address.
VipData.setVenuesMap()* - Generates a folium map of nearby venues.
VipData.setVenuesDf()* - Assembles a dataframe of nearby venue data.
VipData.getMenus()* - Parses venue data to isolate menu data.
VipData.setMenusDf()* - Aggregates a dataframe of venue menu data.
VipData.getMenuStats()* - Aggregates a statistical summary of venue menu data.
VipData.setJson()* - Redefines JSON_DATA class variable.
VipData.getJson() - Retrieves JSON-DATA class variable.

VipData.getJsonTokens() - A simple method for retrieving user credentials for the foursquare, census bureau and nominatim api endpoints.
VipData.start() # This method simply batches a collection of the above methods marked with an asterisk.  
