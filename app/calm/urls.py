from django.urls import path,include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'guides', views.GuideViewSet, basename='guide')
router.register(r'programs', views.ProgramViewSet, basename='program')
router.register(r'emails', views.GuideEmailCampaignViewSet, basename='email')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
