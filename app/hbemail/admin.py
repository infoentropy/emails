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
    # filter_horizontal = ('authors',)

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
admin.site.register(Content)
# admin.site.register(Category)
