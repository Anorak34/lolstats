from django.shortcuts import render, redirect
from django.contrib import messages
import numpy as np
import pandas as pd
from .helpers import gather_data, get_live_game, get_summoner, get_account_stats

regions = ['BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR', 'RU']

def main(request):
    return render(request, 'lolstats/main.html', {})

def champ_stats(request):
    # Maybe not do
    return render(request, 'lolstats/champ_stats.html', {})

def multisearch(request):
    return render(request, 'lolstats/multisearch.html', {})

def player(request):

    # Get user input and direct to player stats page
    player_name = request.GET.get('player_name')
    region = request.GET.get('region')
    return redirect('player_stats', region, player_name)

def player_stats(request, region, player_name):

    # Ensure region and summoner name are valid
    if region not in regions:
        messages.error(request, "ERROR: Invalid Region")
        return redirect('main')
    if not get_summoner(player_name, region):
        messages.error(request, "ERROR: Summoner not found")
        return redirect('main')
    
    if request.GET.get('load_more'):
        try:
            matches = int(request.GET.get('load_more')) + 2
        except:
            messages.error(request, "ERROR: Invalid url")
            return redirect(request.path)

    if player_name in request.session:
        # Check if searched player is stored in session
        data = request.session[player_name]['data']
        match_history = request.session[player_name]['match_history']
        summoner_info = request.session[player_name]['summoner_info']
        account_stats = request.session[player_name]['account_stats']
        # If load more is in url and less matches than needed are stored load more matches and add to current data set otherwise display the amount we want.
        if request.GET.get('load_more'):
            if len(match_history) < matches:
                matches -= len(match_history)
                data2, match_history2, _, _ = gather_data(player_name, region, matches, len(match_history))
                match_history = match_history + match_history2
                for key in data:
                    data[key] = data[key] + data2[key]
                request.session[player_name]['data'] = data
                request.session[player_name]['match_history'] = match_history
            elif len(match_history) > matches:
                matches = len(match_history) - matches
                match_history = match_history[:-matches]
        else:
            if len(match_history) > 2:
                matches = len(match_history) - 2
                match_history = match_history[:-matches]
    else:
        # Run helper function to gather needed data and store in session using base of 10 but if load more is in url load x more than 10
        if not request.GET.get('load_more'):
            data, match_history, summoner_info, account_stats = gather_data(player_name, region, 2)
            request.session[player_name] = {
                'data':data,
                'match_history':match_history,
                'summoner_info':summoner_info,
                'account_stats':account_stats,
            }
        else:
            data, match_history, summoner_info, account_stats = gather_data(player_name, region, matches)
            request.session[player_name] = {
                'data':data,
                'match_history':match_history,
                'summoner_info':summoner_info,
                'account_stats':account_stats,
            }


    # Add winrate to account stats and region to summoner info
    for queue in account_stats:
        queue['winrate'] = queue['wins']/(queue['wins']+queue['losses'])*100
    summoner_info['region'] = region

    # Create data frame for player data to more easily generate stats
    player_data = pd.DataFrame(data)
    player_data['win'] = player_data['win'].astype(int)
    # create a count column
    player_data['count'] = 1
    # Convert game time to minutes
    player_data['time'] = player_data['time'].div(60)

    # Make data frame for champ stats
    champ_df = player_data.groupby('champion').agg({'kills': 'mean', 'deaths': 'mean', 'assists': 'mean', 'win': 'mean', 'count': 'sum'})
    # Reset in the index so we can still use the "champion" column
    champ_df.reset_index(inplace=True)
    # create a kda column
    champ_df['kda'] = round((champ_df['kills'] + champ_df['assists']) / champ_df['deaths'], 2)
    # Create winrate column
    champ_df['win_rate'] = round(champ_df['win'] * 100, 1)
    # Sort by count
    champ_df = champ_df.sort_values('count', ascending=False)

    # Player stats dataframe containing sum, average, average per min and average kda
    cols = ['kills', 'deaths', 'assists', 'minions', 'vision', 'time']
    cols2 = ['kills', 'deaths', 'assists', 'minions', 'vision']
    player_stats_df = player_data[cols].agg(['sum','mean']).rename({'sum':'Total','mean':'Average'})
    player_stats_df.loc['Per min'] = player_stats_df.loc['Average'][cols2] / player_stats_df.loc['Average']['time']
    player_stats_df['kda'] = np.nan
    player_stats_df['kda']['Average'] = (player_stats_df['kills']['Average'] + player_stats_df['assists']['Average']) / player_stats_df['deaths']['Average']
    player_stats_df = round(player_stats_df, 2)

    # Data frame for winrate and record per queue .groupby('queueid').value_counts(['win'])
    queue_df = player_data[['queueid', 'win']]
    queue_df['loss'] = queue_df['win'].apply(lambda x: 1 if x == 0 else 0)
    queue_df = queue_df.groupby('queueid', as_index=False).sum()
    queue_df['winrate'] = queue_df['win'] / (queue_df['win'] + queue_df['loss'])
    
    # Dict for overall winrate
    global_winrate = {
        'win':queue_df['win'].sum(),
        'loss':queue_df['loss'].sum(),
        'winrate':(queue_df['win'].sum() / (queue_df['win'].sum() + queue_df['loss'].sum()))
    }
 
    return render(request, 'lolstats/player_stats.html', {'player_data':player_data, 'match_history':match_history, 'summoner_info':summoner_info, 'account_stats':account_stats})

def player_live(request, region, player_name):
    return render(request, 'lolstats/player_live.html', {})

def view_404(request, exception=None):
    messages.error(request, "ERROR: 404 Not found")
    return redirect('main')