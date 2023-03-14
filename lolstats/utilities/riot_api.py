import os
import requests
import urllib.parse
import time
import asyncio
import aiohttp
from ..utilities.riot_converters import convert_live_runes_and_summs


# Dictionaries containing routing values for RIOT API
platform_routing_values = {'BR':'BR1', 'EUNE':'EUN1', 'EUW':'EUW1', 'JP':'JP1', 'KR':'KR', 'LAN':'LA1', 'LAS':'LA2', 'NA':'NA1', 'OCE':'OC1', 'TR':'TR1', 'RU':'RU'}
regional_routing_values = {'BR':'AMERICAS', 'EUNE':'EUROPE', 'EUW':'EUROPE', 'JP':'ASIA', 'KR':'ASIA', 'LAN':'AMERICAS', 'LAS':'AMERICAS', 'NA':'AMERICAS', 'OCE':'SEA', 'TR':'EUROPE', 'RU':'EUROPE'}


# FUNCTIONS THAT COMMUNICATE WITH THE RIOT API

def get_summoner(summoner_name, region):
    """Look up summoner from inputed summoner name. returns ids used for making other api requests in addition to level and icon"""

    # Set routing value from inputed region
    region = platform_routing_values[region.upper()]

    # Contact API
    try:
        attempts = 0
        while True:
            api_key = os.environ.get("API_KEY")
            url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{urllib.parse.quote_plus(summoner_name)}?api_key={api_key}"
            response = requests.get(url)

            if response.status_code != 429:
                break
            if not response.headers['Retry-After']:
                if attempts < 8:
                    time.sleep(2 ** attempts)
                    print(f"sleeping for {2 ** attempts} seconds")
                    attempts += 1
                else:
                    time.sleep(2 ** 7)
                    print(f"sleeping for {2 ** 7} seconds")
            else:
                time.sleep(int(response.headers['Retry-After']))
                print(f"sleeping for {response.headers['Retry-After']} seconds")
        
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        summoner = response.json()
        return summoner
    except (KeyError, TypeError, ValueError):
        return None


def get_match_ids(puuid, region, match_count, start = 0, queue_id = None):
    """Look up match ids from player puuid"""

    # Set routing value from inputed region
    region = regional_routing_values[region.upper()]

    # Contact API
    try:
        attempts = 0
        while True:
            api_key = os.environ.get("API_KEY")
            if not queue_id:
                url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={str(match_count)}&api_key={api_key}"
            else:
                url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={str(queue_id)}&start={start}&count={str(match_count)}&api_key={api_key}"
            response = requests.get(url)

            if response.status_code != 429:
                break
            if not response.headers['Retry-After']:
                if attempts < 8:
                    time.sleep(2 ** attempts)
                    print(f"sleeping for {2 ** attempts} seconds")
                    attempts += 1
                else:
                    time.sleep(2 ** 7)
                    print(f"sleeping for {2 ** 7} seconds")
            else:
                time.sleep(int(response.headers['Retry-After']))
                print(f"sleeping for {response.headers['Retry-After']} seconds")
        
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
        attempts = 0
        while True:
            api_key = os.environ.get("API_KEY")
            url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
            response = requests.get(url)

            if response.status_code != 429:
                break
            if not response.headers['Retry-After']:
                if attempts < 8:
                    time.sleep(2 ** attempts)
                    print(f"sleeping for {2 ** attempts} seconds")
                    attempts += 1
                else:
                    time.sleep(2 ** 7)
                    print(f"sleeping for {2 ** 7} seconds")
            else:
                time.sleep(int(response.headers['Retry-After']))
                print(f"sleeping for {response.headers['Retry-After']} seconds")
        
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        match_data = response.json()
        return match_data
    except (KeyError, TypeError, ValueError):
        return None


def get_account_stats(id, region):
    """Look up account stats from inputed summoner id. Returns data about account rank"""

    # Set routing value from inputed region
    region = platform_routing_values[region.upper()]

    # Contact API
    try:
        attempts = 0
        while True:
            api_key = os.environ.get("API_KEY")
            url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{id}?api_key={api_key}"
            response = requests.get(url)

            if response.status_code != 429:
                break
            if not response.headers['Retry-After']:
                if attempts < 8:
                    time.sleep(2 ** attempts)
                    print(f"sleeping for {2 ** attempts} seconds")
                    attempts += 1
                else:
                    time.sleep(2 ** 7)
                    print(f"sleeping for {2 ** 7} seconds")
            else:
                time.sleep(int(response.headers['Retry-After']))
                print(f"sleeping for {response.headers['Retry-After']} seconds")
        
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        account = response.json()
        for queue in account:
            queue['winrate'] = queue['wins']/(queue['wins']+queue['losses'])*100
        return account
    except (KeyError, TypeError, ValueError):
        return None


def get_live_game(summoner_name, region):
    """Look up live game from inputed summoner name and convert rune and summonerids"""

    id = get_summoner(summoner_name, region)['id']

    # Set routing value from inputed region
    region = platform_routing_values[region.upper()]

    # Contact API
    try:
        attempts = 0
        while True:
            api_key = os.environ.get("API_KEY")
            url = f"https://{region}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{id}?api_key={api_key}"
            response = requests.get(url)

            if response.status_code != 429:
                break
            if not response.headers['Retry-After']:
                if attempts < 8:
                    time.sleep(2 ** attempts)
                    print(f"sleeping for {2 ** attempts} seconds")
                    attempts += 1
                else:
                    time.sleep(2 ** 7)
                    print(f"sleeping for {2 ** 7} seconds")
            else:
                time.sleep(int(response.headers['Retry-After']))
                print(f"sleeping for {response.headers['Retry-After']} seconds")

        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        live_game_data = response.json()
        return convert_live_runes_and_summs(live_game_data)
    except (KeyError, TypeError, ValueError):
        return None


# ASYNC RIOT API FUNCTIONS

async def get_match_data_async(match_id, region, session):
    """Look up match data from match id"""

    # Set routing value from inputed region
    region = regional_routing_values[region.upper()]

    try:
        attempts = 0
        while True:
            api_key = os.environ.get("API_KEY")
            url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
            
            async with session.get(url) as response:
                if response.status != 429:
                    match_data = await response.json()
                    break
                if not response.headers['Retry-After']:
                    if attempts < 8:
                        time.sleep(2 ** attempts)
                        print(f"sleeping for {2 ** attempts} seconds")
                        attempts += 1
                    else:
                        time.sleep(2 ** 7)
                        print(f"sleeping for {2 ** 7} seconds")
                else:
                    time.sleep(int(response.headers['Retry-After']))
                    print(f"sleeping for {response.headers['Retry-After']} seconds")
        response.raise_for_status()
    except Exception:
        return None
    else:
        return match_data


async def get_summoner_async(summoner_name, region, session):
    """Look up summoner from inputed summoner name. returns ids used for making other api requests in addition to level and icon"""

    # Set routing value from inputed region
    region = platform_routing_values[region.upper()]

    try:
        attempts = 0
        while True:
            api_key = os.environ.get("API_KEY")
            url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{urllib.parse.quote_plus(summoner_name)}?api_key={api_key}"

            async with session.get(url) as response:
                if response.status != 429:
                    summoner = await response.json()
                    break
                if not response.headers['Retry-After']:
                    if attempts < 8:
                        time.sleep(2 ** attempts)
                        print(f"sleeping for {2 ** attempts} seconds")
                        attempts += 1
                    else:
                        time.sleep(2 ** 7)
                        print(f"sleeping for {2 ** 7} seconds")
                else:
                    time.sleep(int(response.headers['Retry-After']))
                    print(f"sleeping for {response.headers['Retry-After']} seconds")
        response.raise_for_status()
    except Exception:
        return None
    else:
        return summoner


async def get_account_stats_async(id, region, session):
    """Look up account stats from inputed summoner id. Returns data about account rank"""

    # Set routing value from inputed region
    region = platform_routing_values[region.upper()]

    try:
        attempts = 0
        while True:
            api_key = os.environ.get("API_KEY")
            url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{id}?api_key={api_key}"
            
            async with session.get(url) as response:
                if response.status != 429:
                    account = await response.json()
                    break
                if not response.headers['Retry-After']:
                    if attempts < 8:
                        time.sleep(2 ** attempts)
                        print(f"sleeping for {2 ** attempts} seconds")
                        attempts += 1
                    else:
                        time.sleep(2 ** 7)
                        print(f"sleeping for {2 ** 7} seconds")
                else:
                    time.sleep(int(response.headers['Retry-After']))
                    print(f"sleeping for {response.headers['Retry-After']} seconds")
        response.raise_for_status()
    except Exception:
        return None
    else:
        for queue in account:
            queue['winrate'] = queue['wins']/(queue['wins']+queue['losses'])*100
        return account


# ASYNC
async def get_async_tasks(data_set, region, function):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for data in data_set:
            task = asyncio.ensure_future(function(data, region, session))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
    return responses


def get_multi_players_async(player_names, region):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_async_tasks(player_names, region, get_summoner_async))
    loop.run_until_complete(future)
    summoner_info_list = future.result()
    return summoner_info_list


def get_multi_accounts_async(summoner_ids, region):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_async_tasks(summoner_ids, region, get_account_stats_async))
    loop.run_until_complete(future)
    account_stats_list = future.result()
    return account_stats_list