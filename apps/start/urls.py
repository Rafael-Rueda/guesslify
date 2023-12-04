from django.urls import path

from apps.start import views

app_name = 'start'

urlpatterns = [
    path('', views.home, name='home'),
    path('spotify-auth/', views.spotify_auth, name='spotify_auth'),
    path('delete_user/', views.delete_user, name='delete_user'),
]
