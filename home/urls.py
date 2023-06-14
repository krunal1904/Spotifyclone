# from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path("",views.index,name='home'),
    path("search", views.search,name='search'),
    path("index", views.index,name='home'),
    path("signup", views.signup,name='signup'),
    path('spotify-login', views.spotify_login, name='spotify-login'),
    path('redirect', views.spotify_callback, name='spotify-callback'),
]
                 