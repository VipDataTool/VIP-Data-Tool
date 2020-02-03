# VIP DATA TOOL

A Very Important Data Tool For Very Important Data Tools!

PURPOSE:  
Listen up chumps- I'M VERY IMPORTANT. MY TIME IS VALUABLE. I'M A BIG DEAL! So when I deserve data, I demand data! That's why I made this very superior, very important data tool for me and my bro's to use when looking for new clubs and bars and stuff to totally dominate...  
  
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
  
I also included a simple static method titled 'VipDt.getJsonTokens()' for retrieving one's credentials from a json document titled "certificate" located in the directory of the script. This method is far from a secure means of storing one's user credentials, and only intended to be used as a very short-term solution in a secure environment. Be sure to '.gitignore' this file if you intend to use this method as to avoid publishing your private API credentials on a public repository.  
  
USER DATA OBJECTS:  
VipDt.JSON_DATA  
VipDt.REPORTS  
  
USER METHODS:  
VipDt.getVenues()*  
VipDt.setVenuesMap()*  
VipDt.setVenuesDf()*  
VipDt.getMenus()*  
VipDt.setMenusDf()*  
VipDt.getMenuStats()*  
VipDt.setJson()*  
VipDt.getJson()

VipDt.getJsonTokens()  
VipDt.start() # This method simply batches a collection of the above methods marked with an asterisk.  
  
CONCLUSIONS:  
I thank me for my time and effort! Special thanks to my crew for the extra creatine and spray tans.
