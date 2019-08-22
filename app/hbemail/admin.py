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
YamlContentAdminForm,
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
    readonly_fields = ('openPreview', )
    def openPreview(self, obj):
        url = reverse('template', args=(obj.id, ))
        return format_html('<a href="{}">Preview</a>', url)
    openPreview.allow_tags = True


class ComponentAdmin(admin.ModelAdmin):
    model = Component
    form = ComponentAdminForm
    list_display = ('name', 'category',)
    readonly_fields = ('pretty_json', )

class ContentAdmin(admin.ModelAdmin):
    model = Content
    readonly_fields = ('preview', 'sync_to_iterable', )
    # form = YamlContentAdminForm
    # filter_horizontal = ('authors',)
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = YamlContentAdminForm
        return super().get_form(request, obj, **kwargs)


    def sync_to_iterable(self, obj):
        return format_html('<a href="{}">{}</a>', 'something', 'something')

    sync_to_iterable.allow_tags = True


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
