
function refresh() {
    
  $.ajax({
      url: "./refresh",
      type: "get",
  }).done(function(data, status) {
    console.log(data);
    
    $('.score').html(data.bigs[0] + " - " +  data.bigs[1]);
    
    
    var i = 0;
    $('.game-log').children().each(function () {
      $(this).html(data.plays[i]);
      i ++;
    });
    while (i < data.plays.length) {
      $('.game-log').append('<li>' + data.plays[i] + '</li>');
      i ++;
    }
    	  
    var order = ['hits', 'misses', 'hit_percentage', 'points', 'plinks', 'plunks',
      'catches', 'kicks', 'negative_points', 'self_plunks'];
    	  
    i = 0;
    $('.gamestats tbody').children().each(function () { 
      var h = 0;
      $(this).children('td').each(function () {
        
        $(this).html(data.stats[h][order[i]]);
        h ++;
        
      });
      
      i ++;
      
    });
    
    
    i = 0;
    $('.scoreboard tbody').children().each(function () {
      $(this).children().eq(0).html(data.score[i][0]);
      $(this).children().eq(1).html(data.score[i][1]);
      i ++;
    });
    while (i < data.score.length) {
      $('.scoreboard').append('<tr> <td>' + data.score[i][0] + '</td><td>' + data.score[i][1] + '</td> </tr>');
      i ++;
    }
    
    
    	  
  });
  
  
  
};

window.setInterval(refresh, 5000);