from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import F  
from die.forms import *
from die.models import *
from die.db import *
from datetime import datetime
import hashlib


def index(request):
    
    return render(request, 'index.html');


def game_list(request):
    
    games = NGame.all() 
    # sorting reference: https://stackoverflow.com/questions/18411560/sort-list-while-pushing-none-values-to-the-end
    games = sorted(games, key=lambda x: (x.datetime is None, x.datetime), reverse=False)
    

    players = get_options(NPlayer.all())
    teams = get_options(NLeagueTeam.all())
    
    player_list = []
    team_list = []
    num_filters = 0
    if request.method == "POST":
        form = GameFilter(request.POST, players=players, teams=teams)
        if form.is_valid():
            games = []
            player_list = form.cleaned_data["players"]
            for p in player_list:
                gid = PlayedIn().get_by_b(p)
                for g in gid:
                    games.append(g)
            
            team_list = form.cleaned_data["teams"]
            for t in team_list:
                gid = TeamPlayedIn().get_by_b(t)
                for g in gid:
                    games.append(g)
            
            games = sorted(games, key=lambda x: (x.datetime is None, x.datetime), reverse=False)
    
            num_filters = max(len(player_list), len(team_list))
        
            # get player names
            t_list = []
            for i in player_list:
                player = NPlayer.get({'id': i})
                t_list.append(player.first_name + " " + player.last_name)
            player_list = t_list
            
            t_list = []
            for i in team_list:
                team = NLeagueTeam.get({'id': i})
                t_list.append(team.name)
            team_list = t_list
    
    
    form = GameFilter(players=players, teams=teams)
    return render(request, 'games.html', {'games': games, 'form': form, 'team_filters': team_list, 'player_filters': player_list, 'num_filters': num_filters})
    
def game_detail_big(request, id, big):
    game = NGame.get({'id': id})
    
    teams = TeamPlayedIn.get_by_a(id)
    players = PlayedIn.get_by_a(id)
    
    
    team_1_players = PlaysFor.get_by_b(teams[0].id)
    team_2_players = PlaysFor.get_by_b(teams[1].id)
    
    last_plays = sorted(NToss.filter({"game_id": id}), key=lambda x: (x.datetime is None, x.datetime), reverse=False)
    
      

    stats = []
    players = team_1_players + team_2_players
    
    print("teams", teams, players)

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
    
    if not request.session.has_key('username') or get_user_priv(request.session['username']) < 1:
        return redirect('/games/')
    
    game = NGame.get({"id": id})
    game.delete()
    
    return redirect('/games/')
    
def game_refresh(request, id):
    game = NGame.get({'id': id})
    
    last_plays = sorted(NToss.filter({"game_id": id}), key=lambda x: (x.datetime is None, x.datetime), reverse=False)

    bigs = game.big_score
    plays = render_to_string('gamelog.html', context={'last_plays': last_plays})
    plays = plays.replace("</li>", "")
    plays = plays[plays.find('<li>'):plays.find('</ul>')]
    plays = plays.split('<li>')
    plays = plays[1:]
    
    
    teams = TeamPlayedIn.get_by_a(id)

    team_1_players = PlaysFor.get_by_b(teams[0].id)
    team_2_players = PlaysFor.get_by_b(teams[1].id)
    
    
    players = team_1_players + team_2_players
    
    stats = []
    
    for p in players:
        stats.append(sum_stats(NPlayerBigPointStats.filter({'game_id': id, 'stat_for_player': p.id})))
        stats[-1].player = p  
        
    
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
    

def createAdmin(request):
    exists = False
    if request.method == "POST":
        form = AdminForm(request.POST)
        if form.is_valid():
            admin = NAdmin()
            username = form.cleaned_data['username']
            # if username already exists in table -- don't create
            admin_match = NAdmin().filter({'username': username})
            print(admin_match == None)
            print(admin_match is None)
            if admin_match == None:
                # admin already exists
                exists = True
                pass
            else:
                admin.username = form.cleaned_data['username']
                # hash_pass = hashlib.md5(str(form.cleaned_data['password']).encode("utf-8"))
                
                setattr(admin, "hash", form.cleaned_data['password'])
                admin.privilege = -1

                admin.save()
            
        return render(request, "createAdmin.html", {'form': form, 'exists': exists})
    
    form = AdminForm()
    
    return render(request, 'createAdmin.html', {'form': form})

def login(request):
    login_fail = False
    if request.method == "POST":
        form = AdminForm(request.POST)
        if form.is_valid():
            
            
            auth = authenticate_user(form.cleaned_data['username'], hashlib.md5(str(form.cleaned_data['password']).encode("utf-8")).hexdigest())
            
            if auth:
                request.session['username'] = form.cleaned_data['username']
                return redirect('/')
            else:
                login_fail = True
            
        return render(request, "login.html", {'form': form, 'login_fail': login_fail})
    
    form = AdminForm()
    
    return render(request, 'login.html', {'form': form})

def logout(request):
    
    del request.session['username']
    return redirect('/')
    
def player_list(request):
    players = NPlayer.all()
    return render(request, 'players.html', {'players': players})
    
def player_add(request):
    
    if not request.session.has_key('username') or get_user_priv(request.session['username']) < 1:
        return redirect('/players')
    
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
    
    if not request.session.has_key('username') or get_user_priv(request.session['username']) < 0:
        return redirect('/games/' + str(id))
    
    game = NGame.get({'id': id})
    if game.locked:
        return redirect('/games/' + str(id))
    
    players = get_options(PlayedIn.get_by_a(id))
    
   
    if request.method == 'POST':
        
        form = TossForm(request.POST, players=players)
        # print(form.errors)
        if form.is_valid():
            toss = NToss()
            
            toss.recorded_by = "admin"
            toss.tossed_by = form.cleaned_data['player'][0]
            if len(form.cleaned_data['caught_by']) > 0:
                toss.caught_by = form.cleaned_data['caught_by'][0]
            else:
                toss.caught_by = None
            
            
            if len(form.cleaned_data['kicked_by']) > 0:
                toss.kicked_by = form.cleaned_data['kicked_by'][0]
            else:
                toss.kicked_by = None
            
            
            toss.negative_points = int(form.cleaned_data['negative_points'])
            toss.self_plunked = int(form.cleaned_data['self_plunk'])
            toss.datetime = datetime.now()
            toss.hit = int(form.cleaned_data['hit'])
            toss.dropped = int(form.cleaned_data['dropped'])
            if form.cleaned_data['plink'] is not None:
                # print(form.cleaned_data['plink'])
                toss.plink = int(form.cleaned_data['plink'])
            else:
                toss.plink = 0
                
            toss.plunk = int(form.cleaned_data['plunk'])
            toss.game_id = id
            toss.note = form.cleaned_data['note']
            
            toss.save()
            
            update_game_state(id, toss)
    
    last_plays = sorted(NToss.filter({"game_id": id}), key=lambda x: (x.datetime is None, x.datetime), reverse=True)

            
    scores = game.state
    bigs = game.big_score

    teams = TeamPlayedIn.get_by_a(id)
    
    form = TossForm(players=players)
    
    return render(request, 'stats.html', {'form': form, 'header': 'Recording Stats', 'last_plays': last_plays, 'game': game, 'scores': scores, 'players': players, 'bigs': bigs, 'team_1': teams[0], 'team_2': teams[1]})
  
def stat_delete(request, id):
    
    if not request.session.has_key('username') or get_user_priv(request.session['username']) < 1:
        return redirect('/games/' + str(id))
    
    game = NGame.get({'id': id})
    last_plays = sorted(NToss.filter({"game_id": id}), key=lambda x: (x.datetime is None, x.datetime), reverse=False)[:1]
   
    if len(last_plays) > 0:
        last_plays[0].delete();
        
    rebuild_game_state(id)
        
    return redirect('/games/' + str(id) + "/stats/record")
    
    
def team_add(request, id):
    
    if not request.session.has_key('username') or get_user_priv(request.session['username']) < 1:
        return redirect('/league/' + str(id))
    
    players = get_options(NPlayer.all())
    
    if request.method == 'POST':
        form = LeagueTeamForm(request.POST, players=players)
        
        if form.is_valid():
            team = NLeagueTeam()
            team.name = form.cleaned_data['name']
            # print(form.cleaned_data['players'])
            
            team.part_of_league = id
            
            team.save()
            
            for pid in form.cleaned_data['players']:
                PlaysFor.insert(int(pid), team.id)
        
    
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
    
    if not request.session.has_key('username') or get_user_priv(request.session['username']) < 2:
        return redirect('/leagues/')
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
    
    if not request.session.has_key('username') or get_user_priv(request.session['username']) < 2:
        return redirect('/leagues/')
    league = NLeague.get({'id': id})
    league.delete()
    
    return redirect('/leagues/')
        
def league_game_add(request, id):
    
    if not request.session.has_key('username') or get_user_priv(request.session['username']) < 2:
        return redirect('/league/' + str(id))
        
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
            
            # print(form.cleaned_data)
            
            rebuild_player_stats(1,game)
            
    
    form = LeagueGameForm(league=league, league_teams=get_options(league_teams), players=players)
    
    return render(request, 'addgame.html', {'form': form, 'header': 'Create New League Game', 'teams': teams})
    
def update_game(request, id):
    
    if not request.session.has_key('username') or get_user_priv(request.session['username']) < 1:
        return redirect('/games/' + str(id))
    
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
    
    tosses = sorted(NToss.filter({"game_id": id}), key=lambda x: (x.datetime is None, x.datetime))

    
    
    bigpoint = 1
    bigs = [0, 0]
    littles = [0, 0, bigpoint]
    
    finished_bigs = []
    
    for i in NPlayerBigPointStats.filter({'game_id':id}):
        i.delete()
    
    stats = rebuild_player_stats(bigpoint, game)
    
    for t in tosses:
        team = 1
        player = 0
        kick_player = -1
        caught_player = -1
        
        for i in range(4):
            if t.tossed_by == stats[i].stat_for_player:
                player = i
            if t.kicked_by == stats[i].stat_for_player:
                kick_player = i
            if t.caught_by == stats[i].stat_for_player:
                caught_player = i
                
        if t.tossed_by == stats[0].stat_for_player or t.tossed_by == stats[1].stat_for_player:
            team = 0
        
        
            
        if t.self_plunked:
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
        if t.kicked_by:
            littles[team] -= 1
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
    
    
    # renamed player --> stat_for_player
    
    for i in range(4):
        if t.tossed_by == stats[i].stat_for_player:
            player = i
        if t.kicked_by == stats[i].stat_for_player:
            kick_player = i
        if t.caught_by == stats[i].stat_for_player:
            caught_player = i
            
    if t.tossed_by == stats[0].stat_for_player or t.tossed_by == stats[1].stat_for_player:
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
            # print(player, stats[player].stat_for_player)
            stats[player].points += 1
            stats[player].save()
            # print("points", stats[player].points)
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
        
    # print("point", stats[player].points)
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
    
    
                
def profile(request):

    if request.method == "POST":
        form = AdminUpdateForm(request.POST)
        if form.is_valid():
            admin = NAdmin()
            admin.username = request.session['username']
            
            admin.hash = form.cleaned_data['new_password']
            admin.privilege = get_user_priv(request.session['username'])
            admin.updateA()
        
        return redirect('/profile')
    
    form = AdminUpdateForm()
    
    return render(request, 'profile.html', {'form': form, 'username': request.session['username'], 'privilege': get_user_priv(request.session['username'])} )
    
    
def privileges(request):
    priv_num = get_user_priv(request.session['username'])
    admins = NAdmin.allAdmin()
    y = []
    privs = [(-1, "Unassigned"), (0, "Stat Recorder"), (1, "Tournament Admin"), (2, "Developer")]
    for x in admins:
        y.append( (x[0], x[0]) )
    own_change = False
    change_succ = False
    if request.method == "POST":
        form = ChangePrivilege(request.POST, username=y, privilege=privs)
        if form.is_valid():
            # can't change own role if dev
            if form.cleaned_data['username'] == request.session['username']:
                own_change = True
            else:
                admin = NAdmin()
                admin.username = form.cleaned_data['username']
                admin.privilege = form.cleaned_data['privilege']
                admin.updateAPriv()
                change_succ = True
    
    if str(priv_num) == "2": # developer -- grant access to change form
        form = ChangePrivilege(username=y, privilege=privs)
        return render(request, 'privilege.html', {'priv_num': priv_num, 'form': form, 'own_change': own_change, 'change_succ': change_succ})
    else:
        return render(request, 'privilege.html', {'priv_num': priv_num})