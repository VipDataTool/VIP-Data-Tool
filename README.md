# VIP DATA TOOL

A Very Important Data Tool For Very Important Data Tools!

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
  
I included a simple static method titled 'getJson()' for retrieving one's credentials from a json document titled "certificate,json" located in the root directory of the script. This method is FAR from a secure method of storing one's user credentials, and is only intended to be used as a very short-term solution in a secure environment. Be sure to '.gitignore' this file if you intend to use this method as to avoid publishing your private API credentials on a public repository. For those looking to implement this library in a production environment, I highly recommend storing these credentials as environmental variables and refactoring the provided method as necessary using os.getenv(). Use at your own risk!!
  
USER DATA OBJECTS:  
VipData.JSON_DATA  
VipData.REPORTS  
  
USER METHODS:  
VipData.getVenues()*  
VipData.setVenuesMap()*  
VipData.setVenuesDf()*  
VipData.getMenus()*  
VipData.setMenusDf()*  
VipData.getMenuStats()*  
VipData.setJson()*  
VipData.getJson()

VipData.getJsonTokens()  
VipData.start() # This method simply batches a collection of the above methods marked with an asterisk.  
  
CONCLUSIONS:  
I thank me for my time and effort! Special thanks to my crew for the extra creatine and spray tans.
