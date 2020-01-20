# VIP DATA TOOL

A Very Important Tool For Very Important Tools!

PURPOSE:
LISTEN UP CHUMPS- I'M VERY IMPORTANT. MY TIME IS VALUABLE. I'M A BIG DEAL! So when I deserve data, I demand data! That's why I made this very superior, very important data tool for me and my bro's to use when looking for new clubs and gyms and stuff to totally dominate...  
  
DESCRIPTION:  
V.I.P. stands for "Venues in Places" referring to the Foursquare 'Places' API provided by Foursquare. A description of the endpoint can be found here: <https://developer.foursquare.com/docs/api>  
  
This module is essentially just a wrapper for the Python library referenced here: <https://developer.foursquare.com/docs/api/libraries>  
  
HOW IT WORKS:  
Start by creating an instance of the class object by passing two arguments:  
    1) A string value of an existing address i.e. "123 some st., sometown, somestate, somecountry"  
    2) A dictionary of credentials including the following key values:  
    - "fsid": "Valid Foursquare User Id",  
    - "fssecret" : "Valid Foursquare User Key",  
    - "censuskey" : "Valid US Census API Key"  

The resulting instance can then be treated as a client for querying venue information specific to the area defined by the aforementioned address and a radius dynamically calculated based upon available location demographic data. To query venue data, simply call the 'setter' and 'getter' methods provided to populate the object with resulting data. 

A localized map can be generated from the venue data, as well as dataframes of the subsequent demographic, venue and menu data for further analysis. Instances can be 'pickled' as well, however the Folium objects cannot, but thankfully, maps can easily be regenerated upon deserialization.

USER DICTIONARY OBJECTS:  
VipDt.LOCATION  
VipDt.FS_JSON  
VipDt.FS_SUMMARIES   
VipDt.FS_STATS  
  
USER METHODS:  
VipDt.getVenues()  
VipDt.getVenuesMap()  
VipDt.setVenuesDf()  
VipDt.getMenus()  
VipDt.setMenusDf()  
VipDt.getMenuStats()  
VipDt.setJson()  
VipDt.getJson()  
VipDt.setPickle()  
VipDt.getPickle()  
VipDt.start() # Essentially batch performs a collection of the above methods  
  
I included a simple method titled 'getFileTokens()' for storing the credentials as string values in a text document titled "certificate" located in the directory of the script, however this method is far from a secure means of storing one's user credentials, and therefore should only be used as a short-term solution in a secure environment. Be sure to '.gitignore' this file as well to avoid publishing your private API credentials on a public repository.
  
CONCLUSION:   
I thank me for my time and effort! Special thanks to my crew for the extra creatine and spray tans.
