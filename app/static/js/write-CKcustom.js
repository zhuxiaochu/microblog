var csrf_token = "{{ csrf_token() }}";
console.log(csrf_token)
CKEDITOR.replace('editor1', {
            extraPlugins: 'autogrow,codesnippet,uploadimage,filebrowser',
            autoGrow_minHeight: 200,
            autoGrow_maxHeight: 800,
            autoGrow_bottomSpace: 30,
            codeSnippet_theme: 'monokai_sublime',
            removePlugins: 'resize,emoji',
            language: 'zh-CN,en,ko',
            filebrowserUploadUrl: '/upload',
            uploadUrl: '/upload',
            mathJaxLib: 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS_HTML',
})

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

if (CKEDITOR.env.ie && CKEDITOR.env.version == 8) {
      document.getElementById('ie8-warning').className = 'tip alert';
    }