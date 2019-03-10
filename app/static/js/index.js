$(".category a").click(function(){
    $(".active").removeClass("active");
    $(this).parent().addClass("active");
    var cate = $(this).attr('id')
    $.ajax({
    type: "GET",
    url: 'category/' + cate,
    success: function(msg){
        var xml = msg,
        xmlDoc = $.parseXML( msg ),
        $xml = $( xmlDoc ),
        $article = $xml.find('[num=1]')
        $title = $article.find('title'),
        $time = $article.find('time'),
        $url = $article.find('url'),
        console.log(moment($time.text()).format('YYYY-MM-DD, HH:mm:ss'),
            $title.text(),
            $url.text())
    }
  });
});