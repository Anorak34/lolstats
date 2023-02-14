import os
import requests
import urllib.parse
import pandas as pd

# Dictionaries containing routing values for RIOT API
platform_routing_values = {'BR':'BR1', 'EUNE':'EUN1', 'EUW':'EUW1', 'JP':'JP1', 'KR':'KR', 'LAN':'LA1', 'LAS':'LA2', 'NA':'NA1', 'OCE':'OC1', 'TR':'TR1', 'RU':'RU'}
regional_routing_values = {'BR':'AMERICAS', 'EUNE':'EUROPE', 'EUW':'EUROPE', 'JP':'ASIA', 'KR':'ASIA', 'LAN':'AMERICAS', 'LAS':'AMERICAS', 'NA':'AMERICAS', 'OCE':'SEA', 'TR':'EUROPE', 'RU':'EUROPE'}


def get_puuid(summoner_name, region):
    """Look up puuid from inputed summoner name"""

    # Set routing value from inputed region
    region = platform_routing_values[region]

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
        return summoner["puuid"]
    except (KeyError, TypeError, ValueError):
        return None


def get_match_ids(puuid, region, match_count, queue_id = None):
    """Look up match ids from player puuid"""

    # Set routing value from inputed region
    region = regional_routing_values[region]

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
    region = regional_routing_values[region]

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
    return player_data




def gather_data(summoner_name, region, match_count, queue_id = None):
    puuid = get_puuid(summoner_name, region)
    match_ids = get_match_ids(puuid, region, match_count, queue_id)

    # TODO: Complete funtion
    # Get match and player data using functions in loop
    # Add relevant data to pandas dataframe

    return None



# Maybe implement rate limit error handling into functions that call riot api