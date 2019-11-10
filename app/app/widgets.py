
from mjml.apps import mjml_render
from django import forms
from jinja2 import nodes
from jinja2.ext import Extension


class MjmlExtension(Extension):
    tags = {'mjml'}

    def __init__(self, environment):
        super(MjmlExtension, self).__init__(environment)
        # environment.extend(mjml = '')

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(['name:endmjml'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_mjml'), [], [], body).set_lineno(lineno)

    def _mjml(self, caller):
        try:
            foo = mjml_render(caller())
            return foo
        except Exception as e:
            raise e


class CodeEditor(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super(CodeEditor, self).__init__(*args, **kwargs)
        self.attrs['class'] = 'code-editor'

    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.0/codemirror.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/codemirror.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/mode/xml/xml.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/mode/jinja2/jinja2.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/mode/htmlmixed/htmlmixed.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/mode/django/django.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/mode/yaml/yaml.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/mode/markdown/markdown.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/addon/mode/simple.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/mode/handlebars/handlebars.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/mode/javascript/javascript.js',
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
