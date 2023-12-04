import time

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseGone, HttpResponseNotFound, JsonResponse)
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from spotipy import Spotify, SpotifyOAuth

from apps.game.models import PlaylistControl, QueueMusic, VoteTimer
from apps.rooms.models import Room, TokenForUser, UserInRoom


@csrf_exempt
@login_required(login_url='start:home')
def game_checking_available(request, slug):  
    room = Room.objects.filter(slug=slug).first()
    if not room.available:
        userinroom = UserInRoom.objects.filter(user=request.user).first()
        queue = QueueMusic.objects.filter(room=room).first()
        vote_timer = VoteTimer.objects.filter(room=room).first()
        if queue:
            is_voting = queue.voting
            result_user = queue.queue.user.first_name
        else:
            is_voting = False
            result_user = None

        if vote_timer:
            results = vote_timer.results
        else:
            results = False
        
        if PlaylistControl.objects.filter(blacklisted=False, room=room).exists():
            game_ended = False
        else:
            game_ended = True
        
        return JsonResponse({'started': True, 'is_host': userinroom.host, 'is_voting': is_voting, 'results': results, 'result_user': result_user, 'game_ended': game_ended})
    else:
        return JsonResponse({'started': False})


@csrf_exempt
@login_required(login_url='start:home')
def game_start(request, slug):
    if not request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return HttpResponseBadRequest('Invalid request')
    if request.method == 'POST':
        room = Room.objects.filter(slug=slug).first()
        room.available = False
        room.save()
        return JsonResponse({})
    else:
        messages.error(request, 'An error occurred while starting the game.')
        return redirect('rooms:rooms_joining', slug=slug)

@csrf_exempt
@login_required(login_url='start:home')
def game_running(request, slug):
    if not TokenForUser.objects.filter(user=request.user).exists():
        return HttpResponseBadRequest('Token information is missing.')
    
    room = Room.objects.filter(slug=slug).first()

    # token_info = request.session['token_info']

    # if token_info.get('expires_at', 0) < time.time():
    #         sp_oauth = SpotifyOAuth(
    #             settings.SPOTIFY_CLIENT_ID,
    #             settings.SPOTIFY_CLIENT_SECRET,
    #             settings.SPOTIFY_REDIRECT_URI,
    #             scope="user-library-read user-top-read user-read-playback-state user-read-recently-played",
    #         )
    #         token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    #         request.session['token_info'] = token_info
    
    # sp = Spotify(auth=token_info['access_token'])


    # playlists = sp.current_user_saved_tracks(limit=3) # Change this function based on the needs and modes of the game

    access_token = TokenForUser.objects.filter(user=request.user).first().token

    endpoint_url = 'https://api.spotify.com/v1/me/top/tracks'

    params = {
        'time_range': 'long_term',  # short_term, medium_term, long_term
        'limit': 1,
    }

    response = requests.get(
    endpoint_url,
    headers={'Authorization': 'Bearer ' + access_token},
    params= params
    )

    playlists = response.json()

    players_data = [{'user': player.user.username,'nickname': player.user.first_name, 'host': player.host} for player in UserInRoom.objects.filter(room=room)]

    current_username = request.user.username

    if not PlaylistControl.objects.filter(user=request.user, room=room).exists():
        for track in playlists['items']:
            PC_instance = PlaylistControl.objects.create(user=request.user,
                                        room=room,
                                        playlist_preview_url=track['preview_url'], 
                                        playlist_cover=track['album']['images'][1]['url'], 
                                        playlist_name=track['name'],
                                        playlist_artist=track['artists'][0]['name']
                                        )
            PC_instance.save()

    queue = QueueMusic.objects.filter(room=room).first()

    # return JsonResponse({'playlists': playlists, 'players': players_data, 'current_username': current_username})
    if queue and queue.queue and not queue.ended: # If appear some errors, try removing "and not queue.ended" statement
        music_src = queue.queue.playlist_preview_url
        music_cover = queue.queue.playlist_cover
        music_name = queue.queue.playlist_name
        artist = queue.queue.playlist_artist

        return JsonResponse({'music_src': music_src, 'music_cover': music_cover, 'music_name': music_name, 'music_artist': artist})
    else:
        return HttpResponseNotFound()

@csrf_exempt
@login_required(login_url='start:home')
def game_sort_music(request, slug):
    if request.method == 'POST':
        room = Room.objects.filter(slug=slug).first()

        has_track = PlaylistControl.objects.filter(room=room, blacklisted=False).first()

        # Cant use session because it is individual
        # request.session['queue_music'] = {'track': random_track.playlist_preview_url, 'cover': random_track.playlist_cover, 'name': random_track.playlist_name}
        if has_track:
            if not QueueMusic.objects.filter(room=room).exists():
                track = PlaylistControl.objects.filter(room=room, blacklisted=False).order_by('?').first()
                
                queue_music = QueueMusic.objects.create(room=room, queue=track)
                queue_music.save()

                track.blacklisted = True
                track.save()
            else:
                track = PlaylistControl.objects.filter(room=room, blacklisted=False).order_by('?').first()

                queue_music = QueueMusic.objects.filter(room=room).first()
                queue_music.queue = track
                queue_music.ended = False
                queue_music.save()

                if track:
                    track.blacklisted = True
                    track.save()

        return redirect('game:game_running', slug=slug)
    else:
        return redirect('rooms:rooms_joining', slug=slug)
    
# Vote time

@csrf_exempt
@login_required(login_url='start:home')
def vote_timer(request, slug):
    if request.method == 'POST':
        room = Room.objects.filter(slug=slug).first()
        if room:
            queue = QueueMusic.objects.filter(room=room).first()
            queue.voting = True
            queue.save()

            if (VoteTimer.objects.filter(room=room).exists()):
                timer = VoteTimer.objects.filter(room=room).first()
            else:
                timer = VoteTimer.objects.create(room=room)

            if timer.seconds > 0:
                if (UserInRoom.objects.filter(room=room, host=True).first().user == request.user):
                    timer.seconds = timer.seconds - 1
                    timer.save()
                return JsonResponse({'timing': True, 'seconds': timer.seconds})
            else:
                if (UserInRoom.objects.filter(room=room, host=True).first().user == request.user and request.POST.get('reset') == 'true'):
                    timer.seconds = 15
                    timer.results = True
                    timer.save()

                result_user = QueueMusic.objects.filter(room=room).first().queue.user.first_name
                return JsonResponse({'timing': False, 'result_user': result_user})
            
        else:
            return JsonResponse({})
    else:
        return redirect('rooms:rooms_joining', slug=slug)

@csrf_exempt
@login_required(login_url='start:home')
def set_results_false(request, slug):
    if request.method == 'POST':
        room = Room.objects.filter(slug=slug).first()
        if room:
            timer = VoteTimer.objects.filter(room=room).first()
            timer.results = False
            timer.save()
        return JsonResponse({})
    else:
        return JsonResponse({})

@csrf_exempt
@login_required(login_url='start:home')
def game_ended_music(request, slug):
    if request.method == 'POST':
        room = Room.objects.filter(slug=slug).first()
        queue_music = QueueMusic.objects.filter(room=room).first()
        if room:
            if queue_music:
                if queue_music.ended:
                    return redirect('game:game_checking', slug=slug)
                else:
                    return JsonResponse({'started': False})
            else:
                return JsonResponse({'started': False})
        else:
            return redirect('rooms:rooms')

    else:
        return redirect('rooms:rooms_joining', slug=slug)

@csrf_exempt
@login_required(login_url='start:home')
def game_end_music(request, slug):
    if request.method == 'POST':
        room = Room.objects.filter(slug=slug).first()
        queue_music = QueueMusic.objects.filter(room=room).first()
        queue_music.ended = True
        queue_music.save()
        return redirect('game:game_checking', slug=slug)
    else:
        return redirect('rooms:rooms_joining', slug=slug)
    
def get_all_users_in_room(request, slug):
    room = Room.objects.filter(slug=slug).first()

    if room:
        usersinroom = UserInRoom.objects.filter(room=room)
        all_users_in_room = [user.user.first_name for user in usersinroom]
        return JsonResponse({'all_users_in_room': all_users_in_room})
    else:
        return JsonResponse({})