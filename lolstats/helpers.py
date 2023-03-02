import os
import json
import requests
import urllib.parse
import datetime
import time
import asyncio
import aiohttp

# Dictionaries containing routing values for RIOT API
platform_routing_values = {'BR':'BR1', 'EUNE':'EUN1', 'EUW':'EUW1', 'JP':'JP1', 'KR':'KR', 'LAN':'LA1', 'LAS':'LA2', 'NA':'NA1', 'OCE':'OC1', 'TR':'TR1', 'RU':'RU'}
regional_routing_values = {'BR':'AMERICAS', 'EUNE':'EUROPE', 'EUW':'EUROPE', 'JP':'ASIA', 'KR':'ASIA', 'LAN':'AMERICAS', 'LAS':'AMERICAS', 'NA':'AMERICAS', 'OCE':'SEA', 'TR':'EUROPE', 'RU':'EUROPE'}


# DATA MANIPULATION FUNCTIONS:


def find_player_data(match_data, puuid):
    """Find player data from within match data"""

    participants = match_data['metadata']['participants']
    player_index = participants.index(puuid)
    player_data = match_data['info']['participants'][player_index]

    # Add game type to player data
    player_data['queueId'] = match_data['info']['queueId']
    return player_data

def priority(element):

    # Define sorting order of teams
    if element['teamPosition'] == 'TOP':
        return -5
    if element['teamPosition'] == 'JUNGLE':
        return -4
    if element['teamPosition'] == 'MIDDLE':
        return -3
    if element['teamPosition'] == 'BOTTOM':
        return -2
    if element['teamPosition'] == 'UTILITY':
        return -1
    return 0


def sort_match_data(match_data, puuid):
    """Sort game data by role starting with ally team"""

    sorted_participant_data = []
    sorted_participant_data_enemy = []

    # Get player teams ID
    participants = match_data['metadata']['participants']
    player_index = participants.index(puuid)
    ally_team_id = match_data['info']['participants'][player_index]['teamId']

    # Get participant and team data
    participants = match_data['info']['participants']
    teams = match_data['info']['teams']
    
    
    # Sort participant data
    for participant in participants:
        if participant['teamId'] == ally_team_id:
            sorted_participant_data.append(participant)
        else:
            sorted_participant_data_enemy.append(participant)

    sorted_participant_data = sorted(sorted_participant_data, key=priority)
    sorted_participant_data_enemy = sorted(sorted_participant_data_enemy, key=priority)
    sorted_participant_data = sorted_participant_data + sorted_participant_data_enemy
    
    # Sort team data
    if teams[0]['teamId'] != ally_team_id:
        teams.reverse()

    # Update match data with sorted versions
    match_data['info']['participants'] = sorted_participant_data
    match_data['info']['teams'] = teams

    return match_data


def convert_summs(sum_dd, data):
    """Convert summoner spell id to name"""
    
    for sum in sum_dd:
        if int(sum_dd[sum]['key']) == int(data['summoner1Id']):
            data['summoner1'] = sum_dd[sum]['id']
        if int(sum_dd[sum]['key']) == int(data['summoner2Id']):
            data['summoner2'] = sum_dd[sum]['id']
    return data

def convert_sum_ids(match_history, player_history):
    """Convert summoner spell id to name for match and player history"""

    with open('lolstats/static/json/summoner_dd.json', 'r', encoding='utf-8') as file:
        sum_dd = json.load(file)['data']

    for match_data in match_history:
        participants = match_data['info']['participants']
        for participant in participants:
            participant = convert_summs(sum_dd, participant)
        match_data['info']['participants'] = participants

    for player_data in player_history:
        player_data = convert_summs(sum_dd, player_data)

    return match_history, player_history


def convert_runes(rune_dd, data):
    """Convert rune id to icon path"""
    
    rune_styles = {
        8000:'7201_precision.png',
        8100:'7200_domination.png',
        8200:'7202_sorcery.png',
        8300:'7203_whimsy.png',
        8400:'7204_resolve.png'
    }

    for key in rune_styles:
        if int(data['perks']['styles'][1]['style']) == key:
            data['substyle'] = rune_styles[key]
        
    for rune in rune_dd:
        if int(rune['id']) == int(data['perks']['styles'][0]['selections'][0]['perk']):
            data['keystone'] = rune['iconPath'].replace('/lol-game-data/assets/v1/perk-images/Styles/', '').lower()
    return data


def convert_rune_ids(match_history, player_history):
    """Convert rune id of keystone substyle to icon path"""

    with open('lolstats/static/json/rune_dd.json', 'r', encoding='utf-8') as file:
        rune_dd = json.load(file)

    for match_data in match_history:
        participants = match_data['info']['participants']
        for participant in participants:
            participant = convert_runes(rune_dd, participant)
        match_data['info']['participants'] = participants

    for player_data in player_history:
        player_data = convert_runes(rune_dd, player_data)

    return match_history, player_history


def convert_gameCreation(match_history):
    for match_data in match_history:
        match_data['info']['gameCreation'] = str(datetime.datetime.fromtimestamp(int(match_data['info']['gameCreation'])/1000).date())
    return match_history


def add_team_gold(match_history):
    for match in match_history:
        match['info']['teams'][0]['objectives']['gold'] = 0
        match['info']['teams'][1]['objectives']['gold'] = 0
        for participant in match['info']['participants'][:5]:
            match['info']['teams'][0]['objectives']['gold'] += participant['goldEarned']
        for participant in match['info']['participants'][5:]:
            match['info']['teams'][1]['objectives']['gold'] += participant['goldEarned']
    return match_history


def convert_live_runes_and_summs(data):
    '''Convert summoner spells, runes and champion id for live data'''

    with open('lolstats/static/json/rune_dd.json', 'r', encoding='utf-8') as file:
        rune_dd = json.load(file)

    with open('lolstats/static/json/summoner_dd.json', 'r', encoding='utf-8') as file:
        sum_dd = json.load(file)['data']

    with open('lolstats/static/json/champion_dd.json', 'r', encoding='utf-8') as file:
        champ_dd = json.load(file)['data']

    rune_styles = {
        8000:'7201_precision.png',
        8100:'7200_domination.png',
        8200:'7202_sorcery.png',
        8300:'7203_whimsy.png',
        8400:'7204_resolve.png'
    }

    for participant in data['participants']:
        for key in rune_styles:
            if int(participant['perks']['perkSubStyle']) == key:
                participant['substyle'] = rune_styles[key]
            
        for rune in rune_dd:
            if int(rune['id']) == int(participant['perks']['perkIds'][0]):
                participant['keystone'] = rune['iconPath'].replace('/lol-game-data/assets/v1/perk-images/Styles/', '').lower()

        for sum in sum_dd:
            if int(sum_dd[sum]['key']) == int(participant['spell1Id']):
                participant['summoner1'] = sum_dd[sum]['id']
            if int(sum_dd[sum]['key']) == int(participant['spell2Id']):
                participant['summoner2'] = sum_dd[sum]['id']
        
        for champ in champ_dd:
            if int(champ_dd[champ]['key']) == int(participant['championId']):
                participant['championName'] = champ_dd[champ]['id']

    return data


# RIOT API DATA GATHERING FUNCTIONS:


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


# CONSOLIDATION FUNCTIONS:


def gather_data(summoner_name, region, match_count, start = 0, queue_id = None):
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
    match_ids = get_match_ids(puuid, region, match_count, start, queue_id)

    # Initialise lists for data on games that will be displayed 
    match_history = []
    player_history = []
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
        match_data = sort_match_data(match_data, puuid)

        # Add match data to match history
        match_history.append(match_data)
        player_history.append(player_data)

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

    match_history, player_history = convert_sum_ids(match_history, player_history)
    match_history, player_history = convert_rune_ids(match_history, player_history)
    match_history = convert_gameCreation(match_history)
    match_history = add_team_gold(match_history)
    
    return data, match_history, summoner_info, account_stats, player_history


# RIOT API DATA GATHERING FUNCTIONS, ASYNC VERSION:


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


# ASYNC TASK GATHERER:


async def get_async_tasks(data_set, region, function):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for data in data_set:
            task = asyncio.ensure_future(function(data, region, session))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
    return responses


# ASYNC CONSOLIDATION FUNCTION:

def gather_data_async(summoner_name, region, match_count, start = 0, queue_id = None):
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
    match_ids = get_match_ids(puuid, region, match_count, start, queue_id)

    # Initialise lists for data on games that will be displayed 
    player_history = []
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

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_async_tasks(match_ids, region, get_match_data_async))
    loop.run_until_complete(future)
    match_history = future.result()

    for match_data in match_history:

        player_data = find_player_data(match_data, puuid)
        match_data = sort_match_data(match_data, puuid)

        player_history.append(player_data)

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

    match_history, player_history = convert_sum_ids(match_history, player_history)
    match_history, player_history = convert_rune_ids(match_history, player_history)
    match_history = convert_gameCreation(match_history)
    match_history = add_team_gold(match_history)
    
    return data, match_history, summoner_info, account_stats, player_history


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