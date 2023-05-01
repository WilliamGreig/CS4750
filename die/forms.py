from django import forms
from die.models import *
from datetime import datetime

class AdminForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30)

class AdminUpdateForm(forms.Form):
    new_password = forms.CharField(max_length=30)

class ChangePrivilege(forms.Form):
    username = forms.ChoiceField(required=True)
    privilege = forms.ChoiceField(required=True)
    
    def __init__(self, *args, **kwargs):
        
        self.username = kwargs.pop('username', None)
        self.privilege = kwargs.pop('privilege', None)
        

        super().__init__(*args, **kwargs)    

        self.fields['username'].choices = self.username
        self.fields['privilege'].choices = self.privilege

class GameFilter(forms.Form):
    teams = forms.MultipleChoiceField(required=False)
    players = forms.MultipleChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        
        self.players = kwargs.pop('players', None)
        self.teams = kwargs.pop('teams', None)
        
        super().__init__(*args, **kwargs)    
        
        
        self.fields['players'].choices = self.players
        self.fields['teams'].choices = self.teams

class PlayerForm(forms.Form):
    
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    
    pledge_class = forms.IntegerField(help_text='Pledge Class Year')
    nickname = forms.CharField(max_length=30, required=False)
    

        
class LeagueTeamForm(forms.Form):
    
    players = forms.MultipleChoiceField()
    name = forms.CharField(max_length=50)
    
    def __init__(self, *args, **kwargs):
        
        self.players = kwargs.pop('players', None)
        
        super().__init__(*args, **kwargs) 
        
        self.fields['players'].choices = self.players
    
    class Meta:
        fields = ['players', 'name']
        widgets = {
            'players': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '10'}),
        }

class LeagueForm(forms.Form):
    
    name = forms.CharField(max_length=50)
    year = forms.IntegerField()
    num_weeks = forms.IntegerField()

class LeagueGameForm(forms.Form):
    
    team_1 = forms.ChoiceField()
    team_2 = forms.ChoiceField()
    
    team_1_player_1 = forms.ChoiceField()
    team_1_player_2 = forms.ChoiceField()
    team_2_player_1 = forms.ChoiceField()
    team_2_player_2 = forms.ChoiceField()
    
    week = forms.IntegerField()
    
    def __init__(self, *args, **kwargs):
        
        self.league = kwargs.pop('league', None)
        self.league_teams = kwargs.pop('league_teams', None)
        self.players = kwargs.pop('players', None)
        
        
        super().__init__(*args, **kwargs)    
        
        
        self.fields['team_1'].choices = self.league_teams
        self.fields['team_2'].choices = self.league_teams
        
        self.fields['team_1_player_1'].choices = self.players
        self.fields['team_1_player_2'].choices = self.players
        self.fields['team_2_player_1'].choices = self.players
        self.fields['team_2_player_2'].choices = self.players

class UpdateGame(forms.Form):
    datetime = forms.DateTimeField(initial=datetime.now, required=False)



class TossForm(forms.Form):
    
    player = forms.MultipleChoiceField(required=True)
    caught_by = forms.MultipleChoiceField(required=False)
    kicked_by = forms.MultipleChoiceField(required=False)
    
    hit = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': "form-check-input"}),label_suffix="")
    miss = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': "form-check-input"}),label_suffix="")
    dropped = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': "form-check-input"}),label_suffix="")
    plink = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Plinks'}),label_suffix="")
    plunk = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': "form-check-input"}),label_suffix="")
    negative_points = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': "form-check-input"}),label_suffix="")
    self_plunk = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': "form-check-input"}),label_suffix="")
    note = forms.CharField(required=False)
    
    
    def __init__(self, *args, **kwargs):
        
        self.players = kwargs.pop('players', None)
        
        super().__init__(*args, **kwargs)    
        
        
        self.fields['player'].choices = self.players
        self.fields['caught_by'].choices = self.players
        self.fields['kicked_by'].choices = self.players

        
    class Meta:
        widgets = {
            'player': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '10'}),
            'caught_by': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '2'}),
            'kicked_by': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '2'}),
            'note': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Other Notes'}),
        }