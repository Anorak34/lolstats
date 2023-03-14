import json
import datetime

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
