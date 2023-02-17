from django.shortcuts import render, redirect
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

    # TODO: at end empty cache and store data from here in session cache then add contintional when visiting the page to check if data from searched player is in cache.
    # If yes, then append new data to existing data and use that (use search query to make sure that the user wants more data and is not just revisiing the page)

    # Ensure region and summoner name are valid
    if region not in regions:
        return redirect('main')
    if not get_summoner(player_name, region):
        return redirect('main')
    
    # Run helper function to gather needed data
    data, match_history, summoner_info, account_stats = gather_data(player_name, region, 1)

    # Add winrate to account stats
    for queue in account_stats:
        queue['winrate'] = queue['wins']/(queue['wins']+queue['losses'])*100
    summoner_info['region'] = region

    # Create data frame for player data to more easily generate stats
    player_data = pd.DataFrame(data)
    player_data['win'] = player_data['win'].astype(int)
    # create a count column
    player_data['count'] = 1 

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
    
    return render(request, 'lolstats/player_stats.html', {'player_data':player_data, 'match_history':match_history, 'summoner_info':summoner_info, 'account_stats':account_stats})

def player_live(request, region, player_name):
    return render(request, 'lolstats/player_live.html', {})

def view_404(request, exception=None):
    return redirect('main')