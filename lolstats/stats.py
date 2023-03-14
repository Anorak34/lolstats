from django.contrib import messages
from django.shortcuts import redirect
import asyncio
import numpy as np
import pandas as pd
from time import gmtime, strftime
from .utilities import riot_converters
from .utilities import riot_api

regions = ['BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR', 'RU']

games = 10; 


class UnableToGetPlayerStats(Exception):
    pass

def gather_data_async(summoner_name, region, match_count, start = 0, queue_id = None):
    """Gather data we need. Return game data to display match history, data frame with player data for player stats and account info for header"""

    # Get data needed for functions and return
    summoner = riot_api.get_summoner(summoner_name, region)
    puuid = summoner['puuid']
    summoner_info = {
        'profileIconId':summoner['profileIconId'],
        'name':summoner['name'],
        'summonerLevel':summoner['summonerLevel']
    }
    account_stats = riot_api.get_account_stats(summoner['id'], region)
    match_ids = riot_api.get_match_ids(puuid, region, match_count, start, queue_id)

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
    future = asyncio.ensure_future(riot_api.get_async_tasks(match_ids, region, riot_api.get_match_data_async))
    loop.run_until_complete(future)
    match_history = future.result()

    for match_data in match_history:

        player_data = riot_converters.find_player_data(match_data, puuid)
        match_data = riot_converters.sort_match_data(match_data, puuid)

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

    match_history, player_history = riot_converters.convert_sum_ids(match_history, player_history)
    match_history, player_history = riot_converters.convert_rune_ids(match_history, player_history)
    match_history = riot_converters.convert_gameCreation(match_history)
    match_history = riot_converters.add_team_gold(match_history)
    
    return data, match_history, summoner_info, account_stats, player_history


def player_data(request, region: str, player_name: str):
    # Ensure region and summoner name are valid
    if region not in regions:
        raise UnableToGetPlayerStats("Invalid Region")
    if not riot_api.get_summoner(player_name, region):
        raise UnableToGetPlayerStats("Summoner not found")
    
    if request.GET.get('load_more'):
        try:
            matches = int(request.GET.get('load_more')) + games
        except:
            messages.error(request, "ERROR: Invalid url")
            return redirect(request.path)

    if player_name in request.session:
        # Check if searched player is stored in session
        data = request.session[player_name]['data']
        match_history = request.session[player_name]['match_history']
        summoner_info = request.session[player_name]['summoner_info']
        account_stats = request.session[player_name]['account_stats']
        player_history = request.session[player_name]['player_history']
        
        # If load more is in url and less matches than needed are stored load more matches and add to current data set otherwise display the amount we want.
        if request.GET.get('load_more'):
            if len(match_history) < matches:
                matches -= len(match_history)
                data2, match_history2, _, _, player_history2 = gather_data_async(player_name, region, matches, len(match_history))
                match_history = match_history + match_history2
                player_history = player_history + player_history2
                for key in data:
                    data[key] = data[key] + data2[key]
                request.session[player_name]['data'] = data
                request.session[player_name]['match_history'] = match_history
                request.session[player_name]['player_history'] = player_history
            elif len(match_history) > matches:
                matches = len(match_history) - matches
                match_history = match_history[:-matches]
                player_history = player_history[:-matches]
        else:
            if len(match_history) > games:
                matches = len(match_history) - games
                match_history = match_history[:-matches]
                player_history = player_history[:-matches]
    else:
        # Run helper function to gather needed data and store in session using base of 10 but if load more is in url load x more than 10
        if not request.GET.get('load_more'):
            data, match_history, summoner_info, account_stats, player_history = gather_data_async(player_name, region, games)
            request.session[player_name] = {
                'data':data,
                'match_history':match_history,
                'summoner_info':summoner_info,
                'account_stats':account_stats,
                'player_history':player_history,
            }
        else:
            data, match_history, summoner_info, account_stats, player_history = gather_data_async(player_name, region, matches)
            request.session[player_name] = {
                'data':data,
                'match_history':match_history,
                'summoner_info':summoner_info,
                'account_stats':account_stats,
                'player_history':player_history,
            }
    return {
        'data':data,
        'match_history':match_history,
        'summoner_info':summoner_info,
        'account_stats':account_stats,
        'player_history':player_history,
    }


def player_stats(data):
    # Create data frame for player data to more easily generate stats
    player_data = pd.DataFrame(data)
    player_data['win'] = player_data['win'].astype(int)
    player_data['count'] = 1
    player_data['time'] = player_data['time'].div(60)

    # Make data frame for champ stats with kda and winrate column, ordered by count
    champ_df = player_data.groupby('champion').agg({'kills': 'mean', 'deaths': 'mean', 'assists': 'mean', 'win': 'mean', 'count': 'sum'})
    champ_df.reset_index(inplace=True)
    champ_df['kda'] = round((champ_df['kills'] + champ_df['assists']) / champ_df['deaths'], 2)
    champ_df['winrate'] = round(champ_df['win'] * 100, 1)
    champ_df = champ_df.sort_values('count', ascending=False)
    champ_df = champ_df.drop(columns=['kills', 'assists', 'deaths', 'win'])
    champ_df['winrate'] = champ_df['winrate'].astype(str) + '%'

    # Player stats dataframe containing sum, average, average per min and average kda
    cols = ['kills', 'deaths', 'assists', 'minions', 'vision', 'time']
    cols2 = ['kills', 'deaths', 'assists', 'minions', 'vision']
    player_stats_df = player_data[cols].agg(['sum','mean']).rename({'sum':'Total','mean':'Average'})
    player_stats_df.loc['Per min'] = player_stats_df.loc['Average'][cols2] / player_stats_df.loc['Average']['time']
    player_stats_df['kda'] = np.nan
    player_stats_df['kda']['Average'] = (player_stats_df['kills']['Average'] + player_stats_df['assists']['Average']) / player_stats_df['deaths']['Average']
    player_stats_df = round(player_stats_df, 2)
    player_stats_df['time']['Total'] = strftime("%H:%M:%S", gmtime(player_stats_df['time']['Total'] * 60))
    player_stats_df['time']['Average'] = strftime("%H:%M:%S", gmtime(player_stats_df['time']['Average'] * 60))
    player_stats_df = player_stats_df.transpose()

    # Data frame for winrate and record per queue
    queue_df = player_data[['queueid', 'win']]
    queue_df['loss'] = queue_df['win'].apply(lambda x: 1 if x == 0 else 0)
    queue_df = queue_df.groupby('queueid', as_index=False).sum()
    queue_df['winrate'] = queue_df['win'] / (queue_df['win'] + queue_df['loss'])*100
    queue_df['winrate'] = round(queue_df['winrate'], 2)
    queue_df['winrate'] = queue_df['winrate'].astype(str) + '%'
    queue_df = queue_df.rename(columns={"queueid": "queue"})

    # Dict for overall winrate
    global_winrate = {
        'win':queue_df['win'].sum(),
        'loss':queue_df['loss'].sum(),
        'winrate':str(round(queue_df['win'].sum() / (queue_df['win'].sum() + queue_df['loss'].sum())*100, 2)) + '%',
        'number_of_games':len(data['champion'])
    }

    return {
        'champ_df':champ_df,
        'player_stats_df':player_stats_df, 
        'queue_df':queue_df, 
        'global_winrate':global_winrate,
    }


def player_live(request, region: str, player_name: str):
    # Ensure region and summoner name are valid
    if region not in regions:
        raise UnableToGetPlayerStats("Invalid Region")
    if not riot_api.get_summoner(player_name, region):
        raise UnableToGetPlayerStats("Summoner not found")
    
    if player_name in request.session:
        # Check if searched player is stored in session
        summoner_info = request.session[player_name]['summoner_info']
        account_stats = request.session[player_name]['account_stats']
    else:
        summoner_info = riot_api.get_summoner(player_name, region)
        account_stats = riot_api.get_account_stats(summoner_info['id'], region)
    
    live_game_data = riot_api.get_live_game(player_name, region)

    return {
        'live_game_data':live_game_data, 
        'summoner_info':summoner_info, 
        'account_stats':account_stats
    }


def multisearch(request):
    player_names = request.POST.get('player_names')
    region = request.POST.get('region')
    
    if region not in regions:
        raise UnableToGetPlayerStats("Invalid Region")
    if not player_names:
        raise UnableToGetPlayerStats("Must enter summoner")
    
    player_names = player_names.split(',')
    
    summoner_info_list_initial = riot_api.get_multi_players_async(player_names, region)
    summoner_info_list = []
    summoner_ids = []
    for player, summoner_info in zip(player_names, summoner_info_list_initial):
        if not summoner_info:
            messages.error(request, f"ERROR: {player} not found in {region} server")
        else:
            summoner_ids.append(summoner_info['id'])
            summoner_info_list.append(summoner_info)
    if summoner_ids:
        account_stats_list = riot_api.get_multi_accounts_async(summoner_ids, region)
    if not summoner_info_list:
        raise UnableToGetPlayerStats("No players found")
    
    return {
        'summoner_info_list':summoner_info_list, 
        'account_stats_list':account_stats_list,
        'region':region
    }