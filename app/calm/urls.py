from django.urls import path,include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'guides', views.GuideViewSet)
router.register(r'programs', views.ProgramViewSet)
router.register(r'emails', views.GuideEmailCampaignViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
