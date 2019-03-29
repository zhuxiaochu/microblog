function next() {
  current_num = $("#page_num").text()
  current_num = Number(current_num)
  $.ajax({
    type: "GET",
    url: 'contact',
    data: 'page=' + (current_num + 1).toString(),
    success: function(msg){
                $("#page_num").text(function(i,origin){
                    if (msg === null){
                      alert('error')
                      }
                    else {
                      if (msg[999] != null){
                        $('#prev').first().html('<li class="previous"><a class="" href="#row2" onclick="prev()">上一页</a></li>')
                      };
                      var total = Number(msg[998]);  //real_comments_number
                      for (var i = Number(msg[997]); i > total; i--) {
                        $('#comment' + i.toString()).hide()
                      };
                      if (msg[1000] === 'None'){
                        $('#next').html('<li class="next disabled"><a href="#row2" style="background-color: #e0dede;">没有更多..</a></li>')
                      }
                      for (var i = 0; i < Number(msg[998]); i++) {
                        $('#comment' + (i+1).toString() + ' .user_id').text(msg[i]['user_id'])
                        $('#comment' + (i+1).toString() + ' .content_div').html(msg[i]['content'])
                        $('#comment' + (i+1).toString() + ' .role').text(msg[i]['role'])
                        $('#comment' + (i+1).toString() + ' .leave_time').text(moment(msg[i]['leave_time']).format('YYYY-MM-DD, HH:mm:ss'))
                      };
                    return Number(origin) + 1
                  };
                });
    }
  });
};

function prev(){
  current_num = $("#page_num").text()
  current_num = Number(current_num)
  $.ajax({
    type: "GET",
    url: 'contact',
    data: 'page=' + (current_num - 1).toString(),
    success: function(msg){
                $("#next").html('<li class="next"><a href="#row2" onclick="next()">下一页</a></li>')
                $("#page_num").text(function(i,origin){
                  if (msg === null){
                    alert('no prev!')
                  };
                  if (msg[999] === 'None'){
                    $('#prev').empty()
                  };
                  if ($('.next .disabled') != null) {
                    $('.msgboard').show()
                  };
                  for (var i = 0; i < Number(msg[998]); i++) {
                        $('#comment' + (i+1).toString() + ' .user_id').text(msg[i]['user_id'])
                        $('#comment' + (i+1).toString() + ' .content_div').html(msg[i]['content'])
                        $('#comment' + (i+1).toString() + ' .role').text(msg[i]['role'])
                        $('#comment' + (i+1).toString() + ' .leave_time').text(moment(msg[i]['leave_time']).format('YYYY-MM-DD, HH:mm:ss'))
                      };
                  return Number(origin) - 1
                });
    }
  });
};

