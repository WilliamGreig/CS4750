function findLableForControl(el) {
   var idVal = el.id;
   var labels = document.getElementsByTagName('label');
   for( var i = 0; i < labels.length; i++ ) {
      if (labels[i].htmlFor == idVal)
           return labels[i];
   }
}

function hide_hit() {
    
    document.getElementById("id_miss").checked = true;
    document.getElementById("id_hit").checked = false;
    var elements = ["id_dropped", "id_caught_by", "id_plink", "id_plunk"];
    for (var x in elements) {
        var e = document.getElementById(elements[x]);
        e.disabled = true;
        e.parentElement.hidden = true;
    }
    
    
    
    document.getElementById("id_dropped").checked = false;
    document.getElementById("id_caught_by").value = null;
    document.getElementById("id_plink").value = null;
    document.getElementById("id_plunk").checked = false;
}

function show_hit() {
    document.getElementById("id_miss").checked = false;
    document.getElementById("id_hit").checked = true;
    var elements = ["id_dropped", "id_caught_by", "id_plink", "id_plunk"];
    for (var x in elements) {
        var e = document.getElementById(elements[x]);
        e.disabled = false;
        e.parentElement.hidden = false;
    }
    
}

function hide_miss() {
    document.getElementById("id_miss").checked = false;
    document.getElementById("id_hit").checked = true;
    
    var elements = ["id_kicked_by", "id_self_plunk", "id_negative_points"];
    for (var x in elements) {
        var e = document.getElementById(elements[x]);
        e.disabled = true;
        e.parentElement.hidden = true;
    }
    

    document.getElementById("id_negative_points").checked = false;
    document.getElementById("id_kicked_by").value = null;
    document.getElementById("id_self_plunk").checked = false;
    
}

function show_miss() {
    document.getElementById("id_miss").checked = true;
    document.getElementById("id_hit").checked = false;
    var elements = ["id_kicked_by", "id_self_plunk", "id_negative_points"];
    for (var x in elements) {
        var e = document.getElementById(elements[x]);
        e.disabled = false;
        e.parentElement.hidden = false;
    }
    
}

hide_miss();
show_hit();


document.getElementById("id_hit").addEventListener('input', function (evt) {
    console.log(document.getElementById("id_hit").checked);
    if (document.getElementById("id_hit").checked) {

        
        hide_miss();
        show_hit();
        
    }
    else {
        
        hide_hit();
        show_miss();
        
    }
});


document.getElementById("id_dropped").addEventListener('input', function (evt) {
   if (document.getElementById("id_dropped").checked) {
       document.getElementById("id_caught_by").disabled = true;
       document.getElementById("id_caught_by").value = null;
      
       document.getElementById("id_plunk").disabled = true;
       document.getElementById("id_plunk").checked = false;
   }
   else {
       document.getElementById("id_caught_by").disabled = false;
       document.getElementById("id_plunk").disabled = false;
   }
});

document.getElementById("id_caught_by").addEventListener('input', function (evt) {
   if (document.getElementById("id_caught_by").value) {
       document.getElementById("id_dropped").checked = false;
      
       document.getElementById("id_plunk").checked = false;
   }
   else {
       document.getElementById("id_dropped").disabled = false;
       document.getElementById("id_plunk").disabled = false;
   }
});

document.getElementById("id_plunk").addEventListener('input', function (evt) {
   if (document.getElementById("id_plunk").checked) {
       document.getElementById("id_caught_by").disabled = true;
       document.getElementById("id_caught_by").value = null;
      
       document.getElementById("id_dropped").disabled = true;
       document.getElementById("id_dropped").checked = false;

       document.getElementById("id_plink").disabled = true;
       document.getElementById("id_plink").value = null;  
       
       
       
   }
   else {
       document.getElementById("id_caught_by").disabled = false;
       document.getElementById("id_dropped").disabled = false;
       document.getElementById("id_plink").disabled = false;
   }
});

document.getElementById("id_miss").addEventListener('input', function (evt) {
   if (document.getElementById("id_miss").checked) {
       
       show_miss();
       
       hide_hit();
   }
   else {
       
       hide_miss();
       show_hit();
       
       
   }
});

document.getElementById("id_negative_points").addEventListener('input', function (evt) {
   if (document.getElementById("id_negative_points").checked) {

        document.getElementById("id_miss").checked = false;
        document.getElementById("id_self_plunk").checked = false;
       document.getElementById("id_miss").checked = false;
       
        document.getElementById("id_kicked_by").disabled = true;
        document.getElementById("id_kicked_by").value = null;
        
        hide_hit();
        
        document.getElementById("id_kicked_by").disabled = true;
       document.getElementById("id_kicked_by").value = null;
   }
   else {
       
       document.getElementById("id_kicked_by").disabled = false;
       document.getElementById("id_self_plunk").disabled = false;
       
   }
});

document.getElementById("id_self_plunk").addEventListener('input', function (evt) {
   if (document.getElementById("id_self_plunk").checked) {

       document.getElementById("id_miss").checked = false;
       document.getElementById("id_negative_points").checked = false;
       document.getElementById("id_miss").checked = false;

       
       document.getElementById("id_kicked_by").disabled = true;
       document.getElementById("id_kicked_by").value = null;
       
       hide_hit();
       
       document.getElementById("id_kicked_by").disabled = true;
       document.getElementById("id_kicked_by").value = null;
       
   }
   else {
       
       document.getElementById("id_kicked_by").disabled = false;
       document.getElementById("id_negative_points").disabled = false;
       d
       
   }
});

document.getElementById("id_miss").addEventListener('input', function (evt) {
   if (document.getElementById("id_miss").checked) {

       document.getElementById("id_negative_points").checked = false;
       document.getElementById("id_self_plunk").checked = false;
       document.getElementById("id_hit").checked = false;
      
       hide_hit();
       
       document.getElementById("id_kicked_by").disabled = false;
       document.getElementById("id_kicked_by").parentElement.hidden = false;
       
   }
   else {
       
       document.getElementById("id_miss").disabled = false;
       document.getElementById("id_negative_points").disabled = false;
       document.getElementById("id_self_plunk").disabled = false;
       
   }
});

document.getElementById("id_player").addEventListener('input', function (evt) {
    var player = document.getElementById("id_player").value;
    
    
    var caught_by = document.getElementById("id_caught_by").children;
    var kicked_by = document.getElementById("id_kicked_by").children;
    
    
    if (player == teams[0] || player == teams[1]) {
        for (var x in caught_by) {
            if (caught_by[x].value == teams[0] || caught_by[x].value == teams[1]) {
                caught_by[x].disabled = true;
                caught_by[x].hidden = true;
            }
            else {
                caught_by[x].disabled = false;
                caught_by[x].hidden = false;
            }
        }
        for (var x in kicked_by) {
            if (kicked_by[x].value == teams[0] || kicked_by[x].value == teams[1]) {
                kicked_by[x].disabled = true;
                kicked_by[x].hidden = true;
            }
            else {
                kicked_by[x].disabled = false;
                kicked_by[x].hidden = false;
            }
        }
    }
    else {
        for (var x in caught_by) {
            if (caught_by[x].value == teams[2] || caught_by[x].value == teams[3]) {
                caught_by[x].disabled = true;
                caught_by[x].hidden = true;
            }
            else {
                caught_by[x].disabled = false;
                caught_by[x].hidden = false;
            }
        }
        for (var x in kicked_by) {
            if (kicked_by[x].value == teams[2] || kicked_by[x].value == teams[3]) {
                kicked_by[x].disabled = true;
                kicked_by[x].hidden = true;
            }
            else {
                kicked_by[x].disabled = false;
                kicked_by[x].hidden = false;
            }
        }
    }
    
    
});