from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import (BaseTemplate,
Template,
TemplateCategory,
TemplateContent,
Module,
ModuleComponent,
Component,
ComponentCategory,
Content,
)
from .forms import (
TemplateForm,
ContentAdminForm,
ComponentAdminForm,
TemplateContentForm,
)


# Template > Modules > Components > content?


class ModuleComponentInline(admin.TabularInline):
    model = ModuleComponent
    extra = 1

class TemplateContentInline(admin.StackedInline):
    ordering = ('order', )
    model = TemplateContent
    form = TemplateContentForm
    extra = 0

class TemplateAdmin(admin.ModelAdmin):
    model = Template
    form = TemplateForm
    inlines = (TemplateContentInline, )
    list_display = ('name', 'category', )
    readonly_fields = ('openPreview', 'publishToIterable', )
    def publishToIterable(self, obj):
        if obj and obj.id:
            url = reverse('publishTemplate', args=(obj.id, ))
            return format_html('<a href="{}">Publish</a>', url)
        else:
            return "Save first"
    publishToIterable.allow_tags = True

    def openPreview(self, obj):
        if obj and obj.id:
            url = reverse('viewTemplate', args=(obj.id, ))
            return format_html('<a href="{}">Preview</a>', url)
        else:
            return "Save first"
    openPreview.allow_tags = True



class ComponentAdmin(admin.ModelAdmin):
    model = Component
    form = ComponentAdminForm
    list_display = ('name', 'category',)
    readonly_fields = ('pretty_json', )

class ContentAdmin(admin.ModelAdmin):
    model = Content
    list_display = ('name', 'component',)
    readonly_fields = ('preview', )
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = ContentAdminForm
        return super().get_form(request, obj, **kwargs)



class ModuleAdmin(admin.ModelAdmin):
    model = Module
    inlines = (ModuleComponentInline,)


# Register your models here.
# admin.site.register(BaseTemplate)
admin.site.register(Template, TemplateAdmin)
admin.site.register(TemplateCategory)
admin.site.register(Module, ModuleAdmin)
admin.site.register(ComponentCategory)
admin.site.register(Component, ComponentAdmin)
admin.site.register(Content, ContentAdmin)
# admin.site.register(Category)
