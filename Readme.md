Approach:
 Used Selenium for data scrapping due to its diverse features. I have choose this as it allows us to run JS scripts in it.
 Used carious CSS elements to extract data from the html.
 Look at network tab in inspect pannel for the API calls website is making for getting the info of lat, lng of the addresses from the cookies sent to https://portal.grab.com/foodweb/v2/search
 Used imgage element link to get the restaurant id of the restaurants.
 For getting info about estimate delivery time , fees used https://portal.grab.com/foodweb/v2/merchants/{restaurant_id}?latlng=1.396364,103.747462 to grab further information from it.
 Used Python's multiprocessing module to handle restaurant data collection from multiple locations concurrently.

Problems faced during the implementation
 403 Forbidden error: First when I used to scrappe data from the website it always shows the forbidden error. For resolving this issue read various documents and blogs and get to know about "blink-features=AutomationControlled": This specific argument tells Chrome to disable a feature in the Blink rendering engine (which is used by Chrome) that sets a special JavaScript property window.navigator.webdriver to true when the browser is being controlled by automation software. 

 Getting info about the restaurants: Look into various Api calls for getting the info about the restaurant and lat,lng of the location for which we are looking restaurants for.

For Running the code 
 First: Clone the repository to local computer
 Second: pip install selenium 
 Third: python scraping.py