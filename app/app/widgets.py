from django import forms

class CodeEditor(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super(CodeEditor, self).__init__(*args, **kwargs)
        self.attrs['class'] = 'code-editor'

    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/codemirror.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/codemirror.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/mode/xml/xml.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/mode/htmlmixed/htmlmixed.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/mode/yaml/yaml.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/mode/markdown/markdown.js',
            '/static/codemirror.js'
        )


'''
/static/codemirror.js
----
(function(){
    var $ = django.jQuery;
    $(document).ready(function(){
        $('textarea.html-editor').each(function(idx, el){
          console.log($(el).data('mode'));
            CodeMirror.fromTextArea(el, {
                lineNumbers: true,
                mode: $(el).data('mode') || 'htmlmixed'
            });
        });
    });
})();
'''
