# LOLSTATS
#### Video Demo:  <URL HERE>
#### Description:
This project is a statistics website for league of legends built using Django. It uses the RIOT API for data.

It has 3 main pages:
1. Main/title page: This page shows the general title and purpose for the website i.e., search for a summoner. There is also a search box here with a dropdown, the dropdown contains all the games regions, a user should enter the region of the player they are interested in and then enter their name in the search box. Submitting this will send you to the player stats page.
2. Player stats page: This page shows the stats of a searched player, this includes: rank and win-rate in each of the games queues, player stats like kda, play time and champions played and match history. The match history section shows the players stats from a game with a dropdown for the whole matches participants, hovering over items will display a tooltip with the items data and the other players names are links that allow you to visit their pages. On this page there is a link for 'live game' this will direct to another page with displays current game information if the payer is in game. As a base this page will display the last 10 games, but more can be loaded via a button. Stats are computed from all stats saved in cache, initially this will be 10 but will increase if more games are loaded, since these are stored in cache, if the player is revisited before the browser is closed, the stats section will use the max number of games.
3. Multisearch: This page allows you to search for multiple summoners at once. A user should enter the region via the dropdown and the enter a series of player names in the input box separated by commas. Submitting this will display a list of the valid summoners out of those searched, this list contains data like the players rank in different queues, each item in the list serves as a link to their specific player stats page.

Overview of important files:
1. urls.py: contains all valid urls for the site
2. views.py: contains logic for each page (further detail below)
3. helpers.py: contains helper functions for supporting the sites logic, these are mostly functions that all the RIOT API (further detail below)
4. context_processors.py: serves regions and queueids to all pages
5. templates: contains the html for each URL
6. templatetags: here I have created my own templates for use in the site's html, this includes implementing functionality like zip and changing time in seconds to hh:mm:ss
7. static: this contains my static files, including CSS, JavaScript and JSON. The json is json data from riot regarding items, runes and spells, this is needed because the player data from the API represents item, spell and rune data with ids and I need the json as a reference so that I can find images and descriptions for these. (Further detail of the JavaScript below)

JAVASCRIPT DETAILS:
I have 5 JavaScript files in this project:
1. account_colours.js: this sets a class on the players rank so that each tier has a different colour
2. item_tt.js: this generated and places the item tooltips
3. load_ani.js: this shows a load animation when some forms are submitted (this should be reworked using AJAX as the loading animation persists if the user cancels the page loading)
4. queue_ids.js: in some pages queue ids are displayed, this changes them to be that corresponding queues name
5. timer.js: this creates a game timer for the live game data

HELPERS.PY DETAILS:
Helpers.py contains 4 main types of function that are used throughout the site:
1. data manipulation functions: the data from the API must be altered in places to make it more usable, these functions do thinks like: sort the participants in data from a match, add the whole teams total gold to match data, convert summoner ids to their names, identify the searched player within match data and convert the UNIX timestamp for when the game was made into a date
2. API call functions: these get data from the riot APIs, there are many APIs and to use some you need data from others so there are several of these. Each of them handles errors by returning None and handle rate limiting by sleeping if a 429 error is returned. When 429 is returned the API should tell you how long you need to wait, the functions will sleep for this time if told but if that data is missing it will simply back off exponentially up to 2mins.
3. ASYNC API call functions: These are the same as normal API functions but are async, these are for functions that are called many times per URL like match data in the player stats page. These massively increase the speed of the server heavy tasks in Multisearch and player stats.
4. Consolidation function: This gathers all the data needed for player stats from the various APIs, it also uses the data functions to make them usable and creates a dictionary for the specific data of the searched player needed for the stats sections

VIEWS.PY DETAILS:
Here is the logic for each URL, in each if there is user input it is first validated before data is gathered from the APIs. There are also handlers for 404 and 500 errors here. If the system finds an error (user input, 404 or 500) the user is appropriately redirected, and an error notification is flashed.
player stats page: this view is more complex as it has several extra tasks compared to other views. After data is called it is stored in cache, before data is called the cache is checked for the data we want and if present that is used rather than calling the APIs again which increases speed vastly. The cache data before it is used has be checked to make sure there is the amount we need, meaning if there is not enough data, we get the extra data needed from APIs and append it, or if there is too much we cut it down and only send what is necessary to the template. This view also uses pandas to calculate player stats from the raw data.
