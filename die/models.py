from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import datetime

import die.db


class NAdmin(die.db.Model):
    
    fields = {
        'username': 'string',
        'hash': 'string',
        'privilege': 'int',
    }
    
    def __init__(self):
        super().__init__()


class NPlayer(die.db.Model):
    
    fields = {
        'first_name': 'string',
        'last_name': 'string',
        'pledge_class': 'int',
        'nickname': 'string'
    }
    
    def __init__(self):
        super().__init__()
        self.nickname = None

    def __str__(self):
        return self.nickname if self.nickname else (self.first_name + " " + self.last_name)
        

class NPlayerBigPointStats(die.db.Model):
    
    
    fields = {
        'hits': 'int',
        'misses': 'int',
        'points': 'int',
        'plinks': 'int',
        'plunks': 'int',
        'catches': 'int',
        'kicks': 'int',
        'negative_points': 'int',
        'self_plunks': 'int',
        'point_number': 'int',
        'stat_for_player': 'int',
        'game_id': 'int',
        
    }
    
    def __init__(self):
        super().__init__()
        self.hits = 0
        self.misses = 0
        self.points = 0
        self.plinks = 0
        self.plunks = 0
        self.catches = 0
        self.kicks = 0
        self.negative_points = 0
        self.self_plunks = 0
        self.point_number = 1

    



class NGame(die.db.Model):
    
    fields = {
        'week': 'int',
        'datetime': 'datetime',
        'locked': 'int',
        'part_of_league': 'int',
    }
    
    def __init__(self):
        super().__init__()
        self.locked = 0
    
        
    def get_player_stats(self, bigpoint):
        stats = []
        stats = NPlayerBigPointStats.filter({'game_id': self.id, 'point_number': bigpoint})
        
        return stats    
    
    @property
    def in_the_past(self):
        print(datetime.now(), self.datetime)
        if self.datetime == None:
            return False
        return datetime.now() > self.datetime
        
    @property
    def today(self):
        if self.datetime == None:
            return False
        return datetime.now().date() == self.datetime.date()
        
    @property
    def state(self):
        scores = []
    
        bigpoint = 1
        stats = self.get_player_stats(bigpoint)
        while len(stats):
            score = [stats[0].points + stats[1].points - stats[0].negative_points
                    - stats[1].negative_points - stats[2].kicks - stats[3].kicks,
                    stats[2].points + stats[3].points - stats[2].negative_points
                    - stats[3].negative_points - stats[0].kicks - stats[1].kicks, bigpoint]
            
            if stats[0].plunks or stats[1].plunks:
                score[0] = "Plunk"
            
            if stats[2].plunks or stats[3].plunks:
                score[1] = "Plunk"
                
            if stats[0].self_plunks or stats[1].self_plunks:
                score[0] = "Self Plunk"
            
            if stats[2].self_plunks or stats[3].self_plunks:
                score[1] = "Self Plunk"
            
                
            bigpoint += 1 
            stats = self.get_player_stats(bigpoint)
            scores.append(score)    
        return scores

    @property
    def big_score(self):
        scores = self.state
    
        bigs = [0, 0]
        
        for s in scores:
            if s[0] == "Plunk" or s[1] == "Self Plunk" or s[0] != "Self Plunk" and s[1] != "Plunk" and s[0] >= 7 and (s[0] >= s[1] + 2 or self.locked and s[0] > s[1]):
                bigs[0] += 1
                
            if s[1] == "Plunk" or s[0] == "Self Plunk" or s[1] != "Self Plunk" and s[0] != "Plunk" and s[1] >= 7 and (s[1] >= s[0] + 2 or self.locked and s[1] > s[0]):
                bigs[1] += 1
                
        return bigs
    
    def __str__(self):
        teams_ob = TeamPlayedIn.get_by_a(self.id)
        teams = []
        for i in teams_ob:
            teams.append(str(i))
        return " vs. ".join(teams)
    
class NToss(die.db.Model):
    
    fields = {
        'recorded_by': 'string',
        'tossed_by': 'int',
        'caught_by': 'int',
        'kicked_by': 'int',
        'negative_points': 'int',
        'self_plunked': 'int',
        'datetime': 'datetime',
        'hit': 'int',
        'dropped': 'int',
        'plink': 'int',
        'plunk': 'int',
        'game_id': 'int',
        'note': 'string'
        
    }
    
    @property
    def caught_by_player(self):
        return NPlayer.get({'id': self.caught_by})
    
    @property
    def kicked_by_player(self):
        return NPlayer.get({'id': self.kicked_by})
    
    @property
    def player(self):
        return NPlayer.get({'id': self.tossed_by})
    
    def __init__(self):
        super().__init__()
    

        
      
class NLeagueTeam(die.db.Model):
    
    fields = {
        'name': 'string',
        'part_of_league': 'int'
    }
    
    def __init__(self):
        super().__init__()
        
    def __str__(self):
        return self.name

class PlaysFor(die.db.Relationship):
    model_a = NPlayer
    model_b = NLeagueTeam

class PlayedIn(die.db.Relationship):
    model_a = NGame
    model_b = NPlayer

class TeamPlayedIn(die.db.Relationship):
    model_a = NGame
    model_b = NLeagueTeam


class NLeague(die.db.Model):
    
    fields = {
        'name': 'string',
        'year': 'int',
        'num_weeks': 'int'
    }
    
    @property
    def player_stats(self):
        stats = []
    
        teams = NLeagueTeam.filter({'part_of_league': self.id})
        games = NGame.filter({'part_of_league': self.id})
        
        for t in teams:
        
            s = []
            
            players = PlaysFor.get_by_b(t.id)
            
            for p in players:
                s.append(sum_stats(NPlayerBigPointStats.filter({"stat_for_player": p.id})))
                s[-1].player = str(p)
            stats.append(s)
        
        
        return stats
    
    @property
    def team_stats(self):
        stats = []
    
        teams = NLeagueTeam.filter({'part_of_league': self.id})
        for t in teams:
            s = []
            
            
            players = PlaysFor.get_by_b(t.id)
            
            games = TeamPlayedIn.get_by_b(t.id)
            for g in games:
                temp = []
                for p in players:
                    s.append(sum_stats(NPlayerBigPointStats.filter({"stat_for_player":p.id, 'game_id': g.id})))
               
            s = sum_stats(s)
            s.player = str(t)
            stats.append(s)
        
        league_stats = sum_stats(stats)
        league_stats.player = "League Total"
        stats.append(league_stats)
        
        return stats
    
    def __init__(self):
        super().__init__()

    def __str__(self):
        return self.name + " " + str(self.year)

class Stat(object):
    pass



    
def sum_stats(stats):
    
    hits = 0
    misses = 0
    points = 0
    plinks = 0
    plunks = 0
    kicks = 0
    self_plunks = 0
    negative_points = 0
    catches = 0
    
    for i in stats:
        hits += i.hits
        misses += i.misses
        points += i.points
        plinks += i.plinks
        plunks += i.plunks
        kicks += i.kicks
        self_plunks += i.self_plunks
        negative_points += i.negative_points
        catches += i.catches
    
    out = Stat()
    out.hits = hits
    out.misses = misses
    out.points = points
    out.plinks = plinks
    out.plunks = plunks
    out.kicks = kicks
    out.self_plunks = self_plunks
    out.negative_points = negative_points
    out.catches = catches
    
    out.hit_percentage = "N/A"
    if out.hits + out.misses != 0:
        out.hit_percentage = "{:.1f}%".format(float(out.hits) / (out.hits + out.misses) * 100)
        
    
    return out
    
