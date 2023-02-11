from django.shortcuts import render, redirect

def main(request):
    return render(request, 'lolstats/main.html', {})

def champ_stats(request):
    return render(request, 'lolstats/champ_stats.html', {})

def multisearch(request):
    return render(request, 'lolstats/multisearch.html', {})

def player_stats(request, region, player_name):
    return render(request, 'lolstats/player_stats.html', {})

def player_live(request, region, player_name):
    return render(request, 'lolstats/player_live.html', {})

def view_404(request, exception=None):
    return redirect('main')