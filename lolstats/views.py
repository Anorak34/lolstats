from django.shortcuts import render, redirect
from django.contrib import messages
import json
from . import stats

regions = ['BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR', 'RU']


def main(request):
    return render(request, 'lolstats/main.html', {})


def multisearch(request):
    if request.method == "POST":
        try:
            player_data = stats.multisearch(request)
        except stats.UnableToGetPlayerStats as e:
            messages.error(request, f"ERROR: {e}")
            return redirect('main')
        else:
            return render(request, 'lolstats/multisearched.html', {'player_data':player_data})
    else:
        return render(request, 'lolstats/multisearch.html', {})


def player(request):

    # Get user input and direct to player stats page
    player_name = request.GET.get('player_name')
    region = request.GET.get('region')

    # Ensure region and summoner name are valid
    if region not in regions:
        messages.error(request, "ERROR: Invalid Region")
        return redirect('main')
    if not player_name:
        messages.error(request, "ERROR: Must enter summoner")
        return redirect('main')

    return redirect('player_stats', region, player_name)


def player_stats(request, region: str, player_name: str):
    try:
        player_data = stats.player_data(request, region, player_name)
        player_stats = stats.player_stats(player_data['data'])
    except stats.UnableToGetPlayerStats as e:
        messages.error(request, f"ERROR: {e}")
        return redirect('main')

    # Item data needed for JS
    with open('lolstats/static/json/items_dd_alt.json', 'r', encoding='utf-8') as file:
        item_dd = json.load(file)
    
    return render(request, 'lolstats/player_stats.html', {'player_stats':player_stats, 'player_data':player_data, 'region':region, 'item_dd':item_dd})


def player_live(request, region: str, player_name: str):
    try:
        player_data = stats.player_live(request, region, player_name)
    except stats.UnableToGetPlayerStats as e:
        messages.error(request, f"ERROR: {e}")
        return redirect('main')
    else:
        return render(request, 'lolstats/player_live.html', {'player_data':player_data, 'region':region, 'player_name':player_name})


def view_404(request, exception=None):
    messages.error(request, "ERROR: 404 Not found")
    return redirect('main')


def view_500(request, exception=None):
    messages.error(request, "ERROR: 500 Server issue")
    return redirect('main')