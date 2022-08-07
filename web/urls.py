from django.urls import path

from . import views

urlpatterns = [
    path('test/', views.test, name='test'),  # todo
    path('', views.index, name='index'),

    path('models/classic/', views.models_classic, name='models_classic'),

    path('models/author/', views.models_author_list, name='models_author_list'),
    path('models/author/new/', views.models_author_new, name='models_author_new'),
    path('models/author/<int:pk>/', views.models_author_view, name='models_author_view'),

    path('datasets/', views.datasets_list, name='datasets_list'),
    path('datasets/new/', views.datasets_new, name='datasets_new'),
    path('datasets/<int:pk>/edit/', views.datasets_edit, name='datasets_edit'),

    path('docs/', views.docs, name='docs'),
]
