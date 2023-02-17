from django.shortcuts import render, redirect
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
    player_name = request.GET.get('player_name')
    region = request.GET.get('region')
    return redirect('player_stats', region, player_name)

def player_stats(request, region, player_name):
    if region not in regions:
        return redirect('main')
    if not get_summoner(player_name, region):
        return redirect('main')
    
    player_data, match_history, summoner_info, account_stats = gather_data(player_name, region, 1)

    for queue in account_stats:
        queue['winrate'] = queue['wins']/(queue['wins']+queue['losses'])*100
    summoner_info['region'] = region
    
    return render(request, 'lolstats/player_stats.html', {'player_data':player_data, 'match_history':match_history, 'summoner_info':summoner_info, 'account_stats':account_stats})

def player_live(request, region, player_name):
    return render(request, 'lolstats/player_live.html', {})

def view_404(request, exception=None):
    return redirect('main')