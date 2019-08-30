from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('templates', views.templates, name='templates'),
    path('templates/<int:id>', views.viewTemplate, name='viewTemplate'),
    path('templates/<int:id>/publish', views.publish, name='publishTemplate'),
]
