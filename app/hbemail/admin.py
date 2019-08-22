from django.contrib import admin

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
ComponentAdminForm)


# Template > Modules > Components > content?


class ModuleComponentInline(admin.TabularInline):
    model = ModuleComponent
    extra = 1

class TemplateContentInline(admin.TabularInline):
    ordering = ('order', )
    model = TemplateContent
    extra = 0

class TemplateAdmin(admin.ModelAdmin):
    model = Template
    form = TemplateForm
    inlines = (TemplateContentInline, )

class ComponentAdmin(admin.ModelAdmin):
    model = Component
    form = ComponentAdminForm
    list_display = ('name', 'category',)
    readonly_fields = ('pretty_json', )
    # filter_horizontal = ('authors',)

class ContentAdmin(admin.ModelAdmin):
    model = Content
    readonly_fields = ('preview', )
    # form = YamlContentAdminForm
    # filter_horizontal = ('authors',)
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = YamlContentAdminForm
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
