"""Django app urls."""
from django.conf.urls import url, include

from .views import calculate

urlpatterns = [
    url(r'^eval/', calculate, name='evaluate'),
]
