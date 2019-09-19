from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name = 'index'),
    path('', views.templates, name='templates'),
    path('<int:id>', views.viewTemplate, name='viewTemplate'),
    path('<int:id>/publish', views.publish, name='publishTemplate'),
]
