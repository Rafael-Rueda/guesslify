import random
import string
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from spotipy import CacheHandler, Spotify
from spotipy.oauth2 import SpotifyOAuth

from apps.rooms import models
from apps.start import forms


def generate_unique_state_parameter_for_user(user):
    # Use user-specific information to create a unique string
    user_info = f"{user.id}-{user.username}"  # Customize this based on your user model
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return f"{user_info}-{random_string}"


def home(request):
    rooms_available = models.Room.objects.all().count()

    if 'nicknamedata' in request.session:
        form = forms.NicknameForm(request.session['nicknamedata'])
        del request.session['nicknamedata']
    else:
        form = forms.NicknameForm()

    request.session.clear()

    return render(request, 'start/pages/homepage.html', {'rooms_available': rooms_available, 'form': form})

def spotify_auth(request):
    if 'token_info' in request.session:
        del request.session['token_info']

    client_id = settings.SPOTIFY_CLIENT_ID
    redirect_uri = 'http://localhost:8000/rooms/'

    scope = 'user-library-read user-top-read user-read-playback-state user-read-recently-played'

    url = 'https://accounts.spotify.com/authorize'
    url += '?response_type=token'
    url += '&client_id=' + client_id
    url += '&scope=' + scope
    url += '&redirect_uri=' + redirect_uri

    response = requests.get(url)

    return redirect(response.url)

    # sp_oauth = SpotifyOAuth(
    #     settings.SPOTIFY_CLIENT_ID,
    #     settings.SPOTIFY_CLIENT_SECRET,
    #     settings.SPOTIFY_REDIRECT_URI,
    #     scope="user-library-read user-top-read user-read-playback-state user-read-recently-played",
    # )
    
    # auth_url = sp_oauth.get_authorize_url()

    # return redirect(auth_url)

def delete_user(request):
    if not request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return HttpResponseBadRequest('Invalid request')
    if request.method == 'GET':
        user_to_delete = User.objects.get(username=request.user.username)
        user_to_delete.delete()
        return redirect('start:home')