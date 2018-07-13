from django.urls import path
from . import views

urlpatterns = [
    path('', views.viaView.as_view(), name='index'),
]