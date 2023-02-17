import os
import requests
import urllib.parse
import pandas as pd

# Dictionaries containing routing values for RIOT API
platform_routing_values = {'BR':'BR1', 'EUNE':'EUN1', 'EUW':'EUW1', 'JP':'JP1', 'KR':'KR', 'LAN':'LA1', 'LAS':'LA2', 'NA':'NA1', 'OCE':'OC1', 'TR':'TR1', 'RU':'RU'}
regional_routing_values = {'BR':'AMERICAS', 'EUNE':'EUROPE', 'EUW':'EUROPE', 'JP':'ASIA', 'KR':'ASIA', 'LAN':'AMERICAS', 'LAS':'AMERICAS', 'NA':'AMERICAS', 'OCE':'SEA', 'TR':'EUROPE', 'RU':'EUROPE'}


def get_summoner(summoner_name, region):
    """Look up summoner from inputed summoner name. returns ids used for making other api requests in addition to level and icon"""

    # Set routing value from inputed region
    region = platform_routing_values[region.upper()]

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{urllib.parse.quote_plus(summoner_name)}?api_key={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        summoner = response.json()
        return summoner
    except (KeyError, TypeError, ValueError):
        return None


def get_match_ids(puuid, region, match_count, queue_id = None):
    """Look up match ids from player puuid"""

    # Set routing value from inputed region
    region = regional_routing_values[region.upper()]

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        if not queue_id:
            url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={str(match_count)}&api_key={api_key}"
        else:
            url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={str(queue_id)}&start=0&count={str(match_count)}&api_key={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        match_ids = response.json()
        return match_ids
    except (KeyError, TypeError, ValueError):
        return None


def get_match_data(match_id, region):
    """Look up match data from match id"""

    # Set routing value from inputed region
    region = regional_routing_values[region.upper()]

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        match_data = response.json()
        return match_data
    except (KeyError, TypeError, ValueError):
        return None


def find_player_data(match_data, puuid):
    """Find player data from within match data"""

    # Game participants puuids are in metadata
    # One will match the puuid we aready have for the player
    # Participamt data is in the same order as the participants in metadata
    # So we can use the index in metadata to get the players data
    participants = match_data['metadata']['participants']
    player_index = participants.index(puuid)
    player_data = match_data['info']['participants'][player_index]

    # Add game type to player data
    player_data['queueId'] = match_data['info']['queueId']
    return player_data


def get_account_stats(id, region):
    """Look up account stats from inputed summoner id. Returns data about account rank"""

    # Set routing value from inputed region
    region = platform_routing_values[region.upper()]

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{id}?api_key={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        account = response.json()
        return account
    except (KeyError, TypeError, ValueError):
        return None




def gather_data(summoner_name, region, match_count, queue_id = None):
    """Gather data we need. Return game data to display match history, data frame with player data for player stats and account info for header"""

    # Get data needed for functions and return
    summoner = get_summoner(summoner_name, region)
    puuid = summoner['puuid']
    summoner_info = {
        'profileIconId':summoner['profileIconId'],
        'name':summoner['name'],
        'summonerLevel':summoner['summonerLevel']
    }
    account_stats = get_account_stats(summoner['id'], region)
    match_ids = get_match_ids(puuid, region, match_count, queue_id)

    # Initialise list for data on games that will be displayed 
    match_history = []
    # Initialise dictionary to store relevant player data for analysis
    data = {
        'champion': [],
        'kills': [],
        'deaths': [],
        'assists': [],
        'win': [],
        'minions':[],
        'vision':[],
        'time':[],
        'queueid':[]
    }

    for match_id in match_ids:
        match_data = get_match_data(match_id, region)
        player_data = find_player_data(match_data, puuid)

        # Add match data to match history
        match_history.append(match_data)

        # Add player data to data set
        data['champion'].append(player_data['championName'])
        data['kills'].append(player_data['kills'])
        data['deaths'].append(player_data['deaths'])
        data['assists'].append(player_data['assists'])
        data['win'].append(player_data['win'])
        data['minions'].append(player_data['totalMinionsKilled'])
        data['vision'].append(player_data['visionScore'])
        data['time'].append(player_data['timePlayed'])
        data['queueid'].append(player_data['queueId'])

    return data, match_history, summoner_info, account_stats


def get_live_game(summoner_name, region):
    """Look up live game from inputed summoner name"""

    id = get_summoner(summoner_name, region)['id']

    # Set routing value from inputed region
    region = platform_routing_values[region.upper()]

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://{region}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{id}?api_key={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        live_game_data = response.json()
        return live_game_data
    except (KeyError, TypeError, ValueError):
        return None


# IMPROVEMENTS:
# Implement rate limit error handling into functions that call riot api
# Implement multithreading to send requests at once and improve loading times