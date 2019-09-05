from django.urls import path,include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'campaigns', views.CampaignViewSet)
router.register(r'snippets', views.SnippetViewSet)
router.register(r'campaignsnippets', views.CampaignSnippetViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
