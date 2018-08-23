from __future__ import unicode_literals
from django.conf.urls import include, url
from . import views_users, views_albums, tests

urlpatterns = [

    # Get directory (eye_color and country)
    url(r'^directory/', include('directory.urls')),

    # Get user albums and create new album depend on method (GET or POST)
    url(r'^users/self/albums$', views_albums.get_albums, name='get_albums'),

    # Create photo in album
    url(r'^users/self/album/(?P<album_id>[a-zA-Z0-9-]+)/photo$', views_albums.create_photo, name='create_photo'),

    # Get album data (with photo), update album and delete album depend on method (GET, PUT or DELETE)
    url(r'^users/self/album/(?P<album_id>[a-zA-Z0-9-]+)$', views_albums.get_album, name='get_album'),

    # Update photo and delete photo depend on method (PUT or DELETE)
    url(r'^users/self/photo/(?P<photo_id>[a-zA-Z0-9-]+)$', views_albums.get_photo, name='get_photo'),

    # Get users data and create new user depend on method (GET or POST)
    url(r'^users$', views_users.get_users, name='get_users_data'),

    # User authorization
    url(r'^users/authorize$', views_users.authorize_user, name='authorize_user'),

    # Get user data and update user depend on method (GET or PUT)
    url(r'^users/self$', views_users.get_user, name='get_user'),
]