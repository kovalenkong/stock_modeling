from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('datasets', views.DatasetView, 'datasets')
router.register('algorithms', views.AlgorithmView, 'algorithms')

urlpatterns = [
    path('', include(router.urls)),
    path('build/classic/', views.build_classic_model, name='build_classic'),
    path('build/author/', views.build_author_model, name='build_author'),
]
