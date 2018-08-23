from __future__ import unicode_literals
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^eye_colors$', views.get_eye_colors, name='get_eye_colors'),
    url(r'^countries$', views.get_countries, name='get_countries'),
]