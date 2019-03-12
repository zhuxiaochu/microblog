$(".category a").click(function(){
    $(".active").removeClass("active");
    $(this).parent().addClass("active");
    var cate_id = $(this).attr('id');
    $.ajax({
    type: "GET",
    url: '/category',  /*only need number*/
    data: {cat_id:cate_id.slice(4)},
    success: function(msg){
        xmlDoc = $.parseXML( msg ),
        $xml = $( xmlDoc );
        $(".page").text(1);
        var exp_num = Number($xml.find('exp_num').text());
        var real_num = Number($xml.find('real_num').text());
        var next_num = $xml.find('next_num').text();
        var prev_num = $xml.find('prev_num').text();
        if (next_num === 'None') {
            $("a.float-right").replaceWith(
                '<a class="float-right" href="#row2" style="background-color: #e0dede;">没有更多..</a>');
        }
        else{
            $("a.float-right").replaceWith(
                '<a class="tn btn-primary float-right" href="#row2" onclick="next()">下一页 →</a>');
        };
        if (prev_num === 'None') {
            $("a.tn.float-left").replaceWith(
                '<a class="tn btn-primary float-left" href=""></a>');
        };
        for (var i = exp_num; i > real_num; i--) {
            $("#post" + i.toString()).hide();
        };
        for (var i = 1; i <= real_num; i++) {
            $article = $xml.find("[num={0}]".replace('{0}',i))
            $title = $article.find('title'),
            $time = $article.find('time'),
            $url = $article.find('url'),
            $content = $article.find('content'),
            $cate = $article.find('cate'),
            $author = $article.find('author'),
            $post = $("#post" + i.toString()),
            $post.show(),
            $post.find('.post-title').text($title.text()),
            $post.find('a:first').attr('href', $url.text()),
            $post.find('.post-subtitle').text($content.text()),
            $post.find('.post-meta a').text($author.text()),
            $post.find('.cate').text($cate.text()),
            $post.find('.time').text(moment($time.text()).format('YYYY-MM-DD, HH:mm:ss'))
        };
    },
    error: function(msg) {
        alert("The XML File could not be processed correctly.");
    },

  });
});

function next() {
  var cat_id = $(".active a").attr('id').slice(4)
  var page = Number($(".page").text())
  $.ajax({
    type: "GET",
    url: '/category',
    data: {cat_id:cat_id,page:(page + 1).toString()},
    success: function(msg){
        xmlDoc = $.parseXML( msg ),
        $xml = $( xmlDoc );
        var exp_num = Number($xml.find('exp_num').text());
        var real_num = Number($xml.find('real_num').text()) - page*exp_num;
        var next_num = $xml.find('next_num').text();
        var prev_num = $xml.find('prev_num').text();
        $(".page").text(page + 1);
        for (var i = exp_num; i > real_num; i--) {
            $("#post" + i.toString()).hide();
        };
        $("a.tn.float-left").replaceWith('<a class="tn btn-primary float-left" href="#row2" onclick="prev()">&larr; 上一页</a>')
        if (next_num === 'None') {
            $("a.float-right").replaceWith(
                '<a class="float-right disabled" href="#row2" style="background-color: #e0dede;">没有更多..</a>');
        }
        else{
            $("a.float-right").replaceWith(
                '<a class="tn btn-primary float-right" href="#row2" onclick="next()">下一页 →</a>');
        };
        for (var i = 1; i <= real_num; i++) {
            $article = $xml.find("[num={0}]".replace('{0}',i))
            $title = $article.find('title'),
            $time = $article.find('time'),
            $url = $article.find('url'),
            $content = $article.find('content'),
            $cate = $article.find('cate'),
            $author = $article.find('author'),
            $post = $("#post" + i.toString()),
            $post.show(),
            $post.find('.post-title').text($title.text()),
            $post.find('a:first').attr('href', $url.text()),
            $post.find('.post-subtitle').text($content.text()),
            $post.find('.post-meta a').text($author.text()),
            $post.find('.cate').text($cate.text()),
            $post.find('.time').text(moment($time.text()).format('YYYY-MM-DD, HH:mm:ss'))
        };
    }
  });
};


function prev() {
  var cat_id = $(".active a").attr('id').slice(4)
  var page = Number($(".page").text())
  $.ajax({
    type: "GET",
    url: '/category',
    data: {cat_id:cat_id,page:(page - 1).toString()},
    success: function(msg){
        xmlDoc = $.parseXML( msg ),
        $xml = $( xmlDoc );
        var exp_num = Number($xml.find('exp_num').text());
        var real_num = exp_num;
        var next_num = $xml.find('next_num').text();
        var prev_num = $xml.find('prev_num').text();
        $(".page").text(page - 1);
        if ($(".disabled").length > 0) {
            $("a.float-right").replaceWith(
                '<a class="tn btn-primary float-right" href="#row2" onclick="next()">下一页 →</a>');
        };
        if (prev_num === 'None') {
            $("a.tn.float-left").replaceWith(
                '<a class="tn btn-primary float-left" href=""></a>');
        }
        else {
            $("a.tn.float-left").replaceWith(
                '<a class="tn btn-primary test float-left" href="#row2" onclick="prev()">&larr; 上一页</a>');
        };
        for (var i = 1; i <= real_num; i++) {
            $article = $xml.find("[num={0}]".replace('{0}',i))
            $title = $article.find('title'),
            $time = $article.find('time'),
            $url = $article.find('url'),
            $content = $article.find('content'),
            $cate = $article.find('cate'),
            $author = $article.find('author'),
            $post = $("#post" + i.toString()),
            $post.show(),
            $post.find('.post-title').text($title.text()),
            $post.find('a:first').attr('href', $url.text()),
            $post.find('.post-subtitle').text($content.text()),
            $post.find('.post-meta a').text($author.text()),
            $post.find('.cate').text($cate.text()),
            $post.find('.time').text(moment($time.text()).format('YYYY-MM-DD, HH:mm:ss'))
        };
    }
  });
};
