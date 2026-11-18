
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

from .views import (
    WebsiteViewSet,
    VisitViewSet,
    PerformanceMetricViewSet
)

router = DefaultRouter()

router.register('websites', WebsiteViewSet)
router.register('visits', VisitViewSet)
router.register('metrics', PerformanceMetricViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path(
    'visits/<int:visit_id>/diagnostics/' ,
    views.run_diagnostics , 
    name='run_diagnostics'
    ),
]


