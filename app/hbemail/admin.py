from django.contrib import admin

from .models import (BaseTemplate,
Template,
TemplateCategory,
TemplateRegion,
Region,
Module,
ModuleComponent,
Component,
ComponentCategory,
Content,
)
from .forms import (YamlContentAdminForm, MarkdownContentAdminForm, ComponentAdminForm)


# Template > Modules > Components > content?


class ModuleComponentInline(admin.TabularInline):
    model = ModuleComponent
    extra = 1

class TemplateRegionInline(admin.TabularInline):
    ordering = ('order', )
    model = TemplateRegion
    extra = 0

class TemplateAdmin(admin.ModelAdmin):
    model = Template
    inlines = (TemplateRegionInline, )

class ComponentAdmin(admin.ModelAdmin):
    model = Component
    form = ComponentAdminForm
    list_display = ('name', 'category',)
    readonly_fields = ('pretty_json', )
    # filter_horizontal = ('authors',)

class ContentAdmin(admin.ModelAdmin):
    model = Content
    readonly_fields = ('preview', )
    # form = ContentAdminForm
    # filter_horizontal = ('authors',)
    def get_form(self, request, obj=None, **kwargs):
        if obj and obj.data_type == 'yaml':
            kwargs['form'] = YamlContentAdminForm
        elif obj and obj.data_type == 'markdown':
            kwargs['form'] = MarkdownContentAdminForm
        return super().get_form(request, obj, **kwargs)

class ModuleAdmin(admin.ModelAdmin):
    model = Module
    inlines = (ModuleComponentInline,)


# Register your models here.
# admin.site.register(BaseTemplate)
admin.site.register(Template, TemplateAdmin)
admin.site.register(TemplateCategory)
admin.site.register(Region)
admin.site.register(Module, ModuleAdmin)
admin.site.register(ComponentCategory)
admin.site.register(Component, ComponentAdmin)
admin.site.register(Content, ContentAdmin)
# admin.site.register(Category)
