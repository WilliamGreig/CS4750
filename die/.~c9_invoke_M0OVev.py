from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import F  
from die.forms import *
from die.models import *
from die.db import *


def index(request):
    
    return render(request, 'index.html');


def game_list(request):
    
    games = NGame.all() 
    # sorting reference: https://stackoverflow.com/questions/18411560/sort-list-while-pushing-none-values-to-the-end
    games = sorted(games, key=lambda x: (x.datetime is None, x.datetime), reverse=False)
    
    return render(request, 'games.html', {'games': games})
    
def game_detail_big(request, id, big):
    game = NGame.get({'id': id})
    
    teams = TeamPlayedIn.get_by_a(id)
    players = set(PlayedIn.get_by_a(id))
    
    
    team_1_players = PlaysFor.get_by_b(teams[0].id)
    team_2_players = PlaysFor.get_by_b(teams[1].id)
    
    players = {}
    last_plays = sorted(NToss.filter({"game_id": id}), key=lambda x: (x.datetime is None, x.datetime), reverse=False)
        

    stats = []
    
    players = team_1_players + team_2_players

    if big == -1:
        for p in players:
            stats.append(sum_stats(NPlayerBigPointStats.filter({'game_id': id, 'stat_for_player': p.id})))
            stats[-1].player = p
            
    else:  
        for p in players:
            stats.append(sum_stats(NPlayerBigPointStats.filter({'game_id': id, 'stat_for_player': p.id, 'point_number': big})))
            stats[-1].player = p
    
    
    bigs = game.big_score
    scores = game.state
    league = NLeague.get({"id":game.part_of_league})
    print(last_plays)
    
    form = UpdateGame()
    
    return render(request, 'game.html', {
        'game': game, 
        'form': form, 
        'last_plays': last_plays, 
        'team_1': teams[0],
        'team_2': teams[1],
        'team_1_players': team_1_players, 
        'team_2_players': team_2_players, 
        'scores': scores, 
        'stats': stats, 
        'bigs': bigs, 
        'league': league,
        })

def game_detail(request, id):
    return game_detail_big(request, id, -1)
    
def game_delete(request, id):
    game = NGame.get({"id": id})
    game.delete()
    
    return redirect('/games/')
    
def game_refresh(request, id):
    game = NGame.get({'id': id})
    
    last_plays = sorted(NToss.filter({"id": id}), key=lambda x: (x.datetime is None, x.datetime), reverse=False)

    bigs = game.big_score
    plays = render_to_string('gamelog.html', context={'last_plays': last_plays})
    plays = plays.replace("</li>", "")
    plays = plays[plays.find('<li>'):plays.find('</ul>')]
    plays = plays.split('<li>')
    plays = plays[1:]
    
    
    stats = [
        sum_stats(PlayerBigPointStats.objects.filter(game=game, player = game.team_1_player_1)),
        sum_stats(PlayerBigPointStats.objects.filter(game=game, player = game.team_1_player_2)),
        sum_stats(PlayerBigPointStats.objects.filter(game=game, player = game.team_2_player_1)),
        sum_stats(PlayerBigPointStats.objects.filter(game=game, player = game.team_2_player_2)),
        ]   
        
    
    stats_serial = []
    for i in stats:
        stats_serial.append({
                'hits': i.hits,
                'misses': i.misses,
                'points': i.points,
                'plinks': i.plinks,
                'plunks': i.plunks,
                'kicks': i.kicks,
                'self_plunks': i.self_plunks,
                'negative_points': i.negative_points,
                'catches': i.catches,
                'hit_percentage': i.hit_percentage,
            })
    
    
    data = {
        'plays': plays,
        'bigs': bigs,
        'stats': stats_serial,
        'score': game.state,
        'bigs': game.big_score,
    }
    
    return JsonResponse(data, safe=False)
    
    
def player_list(request):
    players = NPlayer.all()
    return render(request, 'players.html', {'players': players})
    
def player_add(request):
    
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = NPlayer()
            player.first_name = form.cleaned_data['first_name']
            player.last_name = form.cleaned_data['last_name']
            player.pledge_class = form.cleaned_data['pledge_class']
            player.nickname = form.cleaned_data['nickname']
            
            player.save()
    
    
    form = PlayerForm()
    
    return render(request, 'form.html', {'form': form, 'header': 'Add a Player'})
    
    
def stat_record(request, id):
    game = NGame.get({'id': id})
    if game.locked:
        return redirect('/games/' + str(id))
    
    players = get_options(PlayedIn.get_by_a(id))
    
    last_plays = sorted(NToss.filter({"id": id}), key=lambda x: (x.datetime is None, x.datetime), reverse=False)
    
   
    if request.method == 'POST':
        
        form = TossForm(request.POST, players=players)
        print(form.errors)
        if form.is_valid():
            toss = NToss()
            
            toss.recorded_by = 1
            toss.tossed_by = form.cleaned_data['player'][0]
            toss.caught_by = form.cleaned_data['caught_by'][]
            toss.kicked_by = form.cleaned_data['kicked_by']
            toss.negative_points = form.cleaned_data['negative_points']
            toss.self_plunked = form.cleaned_data['self_plunk']
            toss.datetime = form.cleaned_data['kicked_by']
            toss.hit = form.cleaned_data['hit']
            toss.dropped = form.cleaned_data['dropped']
            toss.plink = form.cleaned_data['plink']
            toss.plunk = form.cleaned_data['plunk']
            toss.game_id = id
            toss.note = form.cleaned_data['note']
            
            toss.save()
            
            # update_game_state(id, toss)

            
    scores = game.state
    bigs = game.big_score

    form = TossForm(players=players)
    
    return render(request, 'stats.html', {'form': form, 'header': 'Recording Stats', 'last_plays': last_plays, 'game': game, 'scores': scores, 'players': players, 'bigs': bigs})
  
def stat_delete(request, id):
    game = NGame.get({'id': id})
    last_plays = sorted(NTossF.filter({"id": id}), key=lambda x: (x.datetime is None, x.datetime), reverse=False)[:1]
    if len(last_plays) > 0:
        last_plays[0].delete();
        
    rebuild_game_state(id)
        
    return redirect('/games/' + str(id) + "/stats/record")
    
    
def team_add(request, id):
    
    players = get_options(NPlayer.all())
    
    if request.method == 'POST':
        form = LeagueTeamForm(request.POST, players=players)
        
        
        if form.is_valid():
            team = NLeagueTeam()
            team.name = form.cleaned_data['name']
            team.part_of_league = id
            
            team.save()
        

    
    form = LeagueTeamForm(players=players)
    return render(request, 'form.html', {'form': form})
 
 
def league_list(request):
    leagues = NLeague.all()
    
    return render(request, 'leagues.html', {'leagues': leagues})
    
def league_detail(request, id):
    league = NLeague.get({'id': id})
    teams = NLeagueTeam.filter({'part_of_league': id})
    games = NGame.filter({'part_of_league': id})
    games = sorted(NGame.filter({'part_of_league': id}), key=lambda x: (x.datetime is None, x.datetime), reverse=False)
    
    team_stats = league.team_stats
    player_stats = league.player_stats
    
    for i in range(len(team_stats) - 1):
        team_stats[i].players = player_stats[i]

    return render(request, 'league.html', {'league': league, 'teams': teams, 'weeks': range(1, league.num_weeks+1), 'games': games, 'team_stats': team_stats})

def league_add(request):
    if request.method == 'POST':
        form = LeagueForm(request.POST)
        if form.is_valid():
            league = NLeague()
            league.name = form.cleaned_data['name']
            league.year = form.cleaned_data['year']
            league.num_weeks = form.cleaned_data['num_weeks']
            
            league.save()
            
    form = LeagueForm()
    return render(request, 'form.html', {'form': form, 'header': 'Create New League'})
        
def league_delete(request, id):
    league = NLeague.get({'id': id})
    league.delete()
    
    return redirect('/leagues/')
        
def league_game_add(request, id):
    
    league = NLeague.get({'id': id})
    
    
    league_teams = NLeagueTeam.filter({'part_of_league': id})
    
    teams = []
    num_teams = league_teams[-1].id
    for i in range(num_teams + 1):
        team = []
        
        if NLeagueTeam.get({'id': i}):
            t = NLeague.get({'id': i})
            players = PlaysFor.get_by_b(i)
            for p in players:
                team.append(p.id)
        teams.append(team)

    players = get_options(NPlayer.all())
    
    if request.method == 'POST':
        form = LeagueGameForm(request.POST, league=league, league_teams=get_options(league_teams), players=players)
        if form.is_valid():

            game = NGame()
            game.week = form.cleaned_data['week']
            game.datetime = None
            game.part_of_league = id
            game.save()
            
            PlayedIn.insert(game.id, form.cleaned_data['team_1_player_1'])
            PlayedIn.insert(game.id, form.cleaned_data['team_1_player_2'])
            PlayedIn.insert(game.id, form.cleaned_data['team_2_player_1'])
            PlayedIn.insert(game.id, form.cleaned_data['team_2_player_2'])
            
            TeamPlayedIn.insert(game.id, form.cleaned_data['team_1'])
            TeamPlayedIn.insert(game.id, form.cleaned_data['team_2'])
            
            print(form.cleaned_data)
            
            rebuild_player_stats(1,game)
            
    
    form = LeagueGameForm(league=league, league_teams=get_options(league_teams), players=players)
    
    return render(request, 'addgame.html', {'form': form, 'header': 'Create New League Game', 'teams': teams})
    
def update_game(request, id):
    game = NGame.get({'id': id})
    
    if game.locked:
        return redirect('/games/' + str(id))
    
    if request.method == 'POST':
        form = UpdateGame(request.POST)
        if form.is_valid():
            game.datetime = form.cleaned_data['datetime']
            game.save()
            
    form = UpdateGame()
    return redirect('/games/' + str(id))
    
    
def rebuild_game_state(id):
    game = NGame.get({'id':id})
    
    tosses = game.toss_set.all().order_by('time')
    
    
    bigpoint = 1
    bigs = [0, 0]
    littles = [0, 0, bigpoint]
    
    finished_bigs = []
    
    PlayerBigPointStats.objects.filter(game=game).delete()
    
    stats = rebuild_player_stats(bigpoint, game)
    
    for t in tosses:
        team = 1
        player = 0
        kick_player = -1
        caught_player = -1
        
        for i in range(4):
            if t.player == stats[i].player:
                player = i
            if t.kicked_by == stats[i].player:
                kick_player = i
            if t.caught_by == stats[i].player:
                caught_player = i
                
        if t.player == stats[0].player or t.player == stats[1].player:
            team = 0
        
        
            
        if t.self_plunk:
            stats[player].self_plunks += 1
            stats[player].save()
            bigs[1-team] += 1
            littles[team] = "Self Plunk"
            finished_bigs.append(littles)
            bigpoint += 1
            littles = [0, 0, bigpoint]
            
            stats = rebuild_player_stats(bigpoint, game)
        
        
        if t.hit:
            stats[player].hits += 1
            stats[player].save()
            if t.plunk:
                stats[player].points += max(7-littles[team], littles[1-team] + 2)
                stats[player].plunks += 1
                stats[player].save()
                bigs[team] += 1
                littles[team] = "Plunk"
                finished_bigs.append(littles)
                bigpoint += 1
                littles = [0, 0, bigpoint]
                
                stats = rebuild_player_stats(bigpoint, game)
                
            if t.dropped:
                stats[player].points += 1
                stats[player].save()
                littles[team] += 1
            if t.plink:
                stats[player].plinks += t.plink
                stats[player].points += t.plink
                stats[player].save()
                littles[team] += t.plink
            if t.caught_by:
                stats[caught_player].catches += 1
                stats[caught_player].save()
        else:
            stats[player].misses += 1
            stats[player].save()
        
        if t.negative_points:
            stats[player].negative_points += t.negative_points
            stats[player].save()
            littles[team] -= t.negative_points
        if t.kicked:
            littles[team] -= t.kicked
            stats[kick_player].kicks += 1
            stats[kick_player].save()
            
        if littles[team] >= 7 and littles[team] - littles[1-team] >= 2 and t.plunk == 0 and bigs[team] < 2:
            bigs[team] += 1
            finished_bigs.append(littles)
            
            bigpoint += 1
            littles = [0, 0, bigpoint]
            
            
            stats = rebuild_player_stats(bigpoint, game)
            
        if littles[1-team] >= 7 and littles[1-team] - littles[team] >= 2 and t.plunk == 0 and bigs[1-team] < 2:
            bigs[1-team] += 1
            finished_bigs.append(littles)
            
            bigpoint += 1
            littles = [0, 0, bigpoint]
            
            stats = rebuild_player_stats(bigpoint, game)
        
    finished_bigs.append(littles)
    return finished_bigs        

def update_game_state(id, t):
    game = NGame.get({'id': id})
    
    bigpoint = 1
    stats = game.get_player_stats(bigpoint)
    while len(stats):
        bigpoint += 1    
        stats = game.get_player_stats(bigpoint)
    bigpoint -= 1
    
    stats = game.get_player_stats(bigpoint)
    
        
    team = 1
    player = 0
    kick_player = -1
    caught_player = -1
    print(stats)
    
    # renamed player --> stat_for_player
    
        if t.player == stats[i].stat_:
        if t.player == stats[i].stat_for_player:
            player = i
        if t.kicked_by == stats[i].stat_for_player:
            kick_player = i
        if t.caught_by == stats[i].stat_for_player:
            caught_player = i
            
    if t.player == stats[0].stat_for_player or t.player == stats[1].stat_for_player:
        team = 0
    
    
        
    if t.self_plunked:
        stats[player].self_plunks += 1
        stats[player].save()
            
        stats = rebuild_player_stats(bigpoint, game)
    
    
    if t.hit:
        stats[player].hits += 1
        stats[player].save()
        if t.plunk:
            stats[player].plunks += 1
            stats[player].save()
            bigpoint += 1
            stats = rebuild_player_stats(bigpoint, game)
            
        if t.dropped:
            stats[player].points += 1
            stats[player].save()
        if t.plink:
            stats[player].plinks += t.plink
            stats[player].points += t.plink
            stats[player].save()
        if t.caught_by:
            stats[caught_player].catches += 1
            stats[caught_player].save()
    else:
        stats[player].misses += 1
        stats[player].save()
    
    if t.negative_points:
        stats[player].negative_points += t.negative_points
        stats[player].save()
    if t.kicked_by:
        stats[kick_player].kicks += 1
        stats[kick_player].save()
        
    scores = game.state
    
    bigs = game.big_score
    
    recent_score = scores[-1]
    if (recent_score[0] - recent_score[1] >= 2 and recent_score[0] >= 7 and bigs[0] <=2) or (recent_score[1] - recent_score[0] >= 2 and recent_score[1] >= 7 and bigs[1] <= 2):
        bigpoint += 1
        stats = rebuild_player_stats(bigpoint, game)



def rebuild_player_stats(bigpoint, game):
    stats = []
    
    
    if not len(NPlayerBigPointStats.filter({'game_id': game.id, 'point_number': bigpoint})) > 0:
        for i in PlayedIn.get_by_a(game.id):
            tmp = NPlayerBigPointStats()
            tmp.stat_for_player = i.id
            tmp.point_number = bigpoint
            tmp.game_id = game.id
            tmp.save()
            stats.append(tmp)
        
      
            
        
    else:
        for i in PlayedIn.get_by_a(game.id):
            stats.append(NPlayerBigPointStats.filter({'game_id': game.id, 'point_number': bigpoint, 'stat_for_player': i.id}))
    
        for i in stats:
            i.hits = 0;
            i.misses = 0;
            i.points = 0;
            i.plinks = 0;
            i.plunks = 0;
            i.kicks = 0;
            i.catches = 0;
            i.self_plunks = 0;
            i.negative_points = 0;
            i.save();
    
    return stats
   
    

def get_league_stats(league):
    
    stats = []
    
    teams = NLeagueTeam.filter({'part_of_league': id})
    for t in teams:
        s = []
        
        
        players = PlaysFor.get_by_b(t.id)
        
        games = TeamPlayedIn.get_by_b(t.id)
        for g in games:
            pass
            #s.append(sum_stats(g.playerbigpointstats_set.filter(player__in=players)))


        s = sum_stats(s)
        s.player = str(t)
        stats.append(s)
    
    league_stats = sum_stats(stats)
    league_stats.player = "League Total"
    stats.append(league_stats)
    
    return stats
    
    
                
        