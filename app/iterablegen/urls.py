from django.urls import path,include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'campaigns', views.CampaignViewSet, basename='campaign')
router.register(r'snippets', views.SnippetViewSet, basename='snippet')
router.register(r'campaignsnippets', views.CampaignSnippetViewSet, basename='campaignsnippet')

urlpatterns = [
    path('', include(router.urls)),
]
