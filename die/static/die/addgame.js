function inList(l, s) {
    for (var i in l) {
        if (l[i] == s) return true;
    }
    return false;
}
document.getElementById("id_team_1").addEventListener('input', function (evt) {
    var team = parseInt(document.getElementById("id_team_1").value);
    
    console.log(team);
    
    var p1 = document.getElementById("id_team_1_player_1").children;
    var p2 = document.getElementById("id_team_1_player_2").children;

    
    
    for (var i in p1) {
        if (inList(teams[team], p1[i].value)) {
            p1[i].hidden = false;
            p1[i].disabled = false;
            
            p2[i].hidden = false;
            p2[i].disabled = false;
        }
        else {
            p1[i].hidden = true;
            p1[i].disabled = true;
            
            p2[i].hidden = true;
            p2[i].disabled = true;
        }
    }
    
    
    
    
});

document.getElementById("id_team_2").addEventListener('input', function (evt) {
    var team = parseInt(document.getElementById("id_team_2").value);
    
    console.log(team);
    
    var p1 = document.getElementById("id_team_2_player_1").children;
    var p2 = document.getElementById("id_team_2_player_2").children;

    
    
    for (var i in p1) {
        if (inList(teams[team], p1[i].value)) {
            p1[i].hidden = false;
            p1[i].disabled = false;
            
            p2[i].hidden = false;
            p2[i].disabled = false;
        }
        else {
            p1[i].hidden = true;
            p1[i].disabled = true;
            
            p2[i].hidden = true;
            p2[i].disabled = true;
        }
    }
    
    
    
    
});
