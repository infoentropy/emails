(function(){
    var $ = django.jQuery;
    $(document).ready(function(){
        $('textarea.code-editor').each(function(idx, el){
            CodeMirror.fromTextArea(el, {
                lineNumbers: true,
                lineWrapping: true,
                mode: $(el).data('mode') || 'htmlmixed'
            });
        });
    });
})();
