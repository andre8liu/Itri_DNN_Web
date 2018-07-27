from django.urls import path
from . import views

urlpatterns = [
    path('', views.jsonToYolo.as_view(), name='index')
]