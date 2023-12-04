import random
import string
import time

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from faker import Faker
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from apps.rooms.forms import CreateRoomForm, JoinPasswordRoomForm
from apps.rooms.models import Room, TokenForUser, UserInRoom
from apps.start.forms import NicknameForm


def rooms_checkin(request):
    if request.method == 'POST':
        form = NicknameForm(request.POST)
        request.session['nicknamedata'] = request.POST

        if form.is_valid():
            fake = Faker()
            username = fake.user_name()
            password = fake.password()
            
            # Create user
            User.objects.create_user(username=username, password=password, first_name=form.cleaned_data['nickname'])

            # Login user
            user_auth = authenticate(
                request,
                username=username,
                password=password
            )

            if user_auth is not None:
                login(request, user_auth)
            else:
                messages.error(request, 'Something got wrong ! Please, try again.')
                redirect('/')

            # Del session nicknamedata
            if 'nicknamedata' in request.session:
                del request.session['nicknamedata']

            request.session['userinfo'] = {
                'username': username,
                'password': password,
                'nickname': form.cleaned_data['nickname'],
            }

            request.session.save()
        return redirect('start:spotify_auth')
    else: 
        return redirect('start:home')

@login_required(login_url='start:home')
def rooms(request):
    if 'access_token' in request.GET:
        access_token = request.GET['access_token']
        
        if not TokenForUser.objects.filter(user=request.user).exists():
            TokenForUser.objects.create(user=request.user, token=access_token)
        

    # if 'code' in request.GET:
    #     sp_oauth_token = SpotifyOAuth(
    #         settings.SPOTIFY_CLIENT_ID,
    #         settings.SPOTIFY_CLIENT_SECRET,
    #         settings.SPOTIFY_REDIRECT_URI,
    #         scope="user-library-read user-top-read user-read-playback-state user-read-recently-played",
    #     )

    #     code = request.GET['code']

    #     token_info = sp_oauth_token.get_access_token(code=code)
    #     print('access token = ', token_info['access_token'])

    #     request.session['token_info'] = token_info

    #     if token_info.get('expires_at', 0) < time.time():
    #         token_info = sp_oauth_token.refresh_access_token(token_info['refresh_token'])
    #         request.session['token_info'] = token_info

    #     sp = Spotify(auth=token_info['access_token'])

    #     playlists = sp.current_user()

    rooms = Room.objects.all().filter(available=True)
    createroomform = CreateRoomForm()

    user_connected = UserInRoom.objects.filter(user=request.user).exists()
    room_connected = UserInRoom.objects.filter(user=request.user).first().room if user_connected else ''

    return render(request, 'rooms/pages/rooms.html', {'rooms': rooms, 'form': createroomform, 'user_connected': user_connected, 'room_connected': room_connected})

@csrf_exempt
@login_required(login_url='start:home')
def rooms_joining(request, slug):
    if request.method == 'GET':
        room = Room.objects.filter(slug=slug).first()
        if room:    
            user_already_in_room = UserInRoom.objects.filter(user=request.user, room=room).first()
            allusersinroom = UserInRoom.objects.filter(room=room)

            if (len(allusersinroom) >= 6) and not user_already_in_room:
                messages.error(request, 'Full room ! Please, choose another room.')
                return redirect('rooms:rooms')
            if not room.available and not user_already_in_room:
                messages.error(request, 'Match currently running ! Please, choose another room.')
                return redirect('rooms:rooms')
            
            password_room_form = JoinPasswordRoomForm()

            if room.password and not user_already_in_room:
                return render(request, 'rooms/pages/password_room.html', {'slug': slug, 'form': password_room_form})
            
            if not UserInRoom.objects.filter(user=request.user).exists():
                userinroom = UserInRoom.objects.create(user=request.user, room=room, host=False)
                userinroom.save()
            else:
                if not UserInRoom.objects.filter(user=request.user, room=room):
                    userinroom = UserInRoom.objects.filter(user=request.user).first()
                    userinroom.delete()
                    userinroom = UserInRoom.objects.create(user=request.user, room=room, host=False)
                    userinroom.save()

            allusersinroom = UserInRoom.objects.filter(room=room)
            user_in_room = UserInRoom.objects.filter(user=request.user, room=room).first()
            is_host = user_in_room.host if user_in_room else False

            return render(request, 'rooms/pages/room.html', {'room': room, 'all_users_in_room': allusersinroom, 'is_host': is_host})
        else:
            messages.error(request, "This room doesn't exist anymore.")
            return redirect('rooms:rooms')
    
    if request.method == 'POST':
        data = request.POST
        room = Room.objects.filter(slug=slug).first()
        if room:
            if (data['password'] == room.password):
                if not UserInRoom.objects.filter(user=request.user).exists():
                    userinroom = UserInRoom.objects.create(user=request.user, room=room, host=False)
                    userinroom.save()
                else:
                    if not UserInRoom.objects.filter(user=request.user, room=room):
                        userinroom = UserInRoom.objects.filter(user=request.user).first()
                        userinroom.delete()
                        userinroom = UserInRoom.objects.create(user=request.user, room=room, host=False)
                        userinroom.save()

                allusersinroom = UserInRoom.objects.filter(room=room)
                user_in_room = UserInRoom.objects.filter(user=request.user, room=room).first()
                is_host = user_in_room.host if user_in_room else False

                return render(request, 'rooms/pages/room.html', {'room': room, 'all_users_in_room': allusersinroom, 'is_host': is_host})
            else:
                messages.error(request, 'The password is incorrect.')
                return redirect('rooms:rooms')
        else:
            messages.error(request, "This room doesn't exist anymore.")
            return redirect('rooms:rooms')

@login_required(login_url='start:home')
def rooms_create(request):
    if request.method == 'POST':
        modelform = CreateRoomForm(request.POST)
        user_already_in_room = UserInRoom.objects.filter(user=request.user).exists()
        if user_already_in_room:
            messages.error(request, 'You are already in a room. Leave the room to create another one.')
            return redirect('rooms:rooms')
        if modelform.is_valid():
            newroom = Room.objects.create(name=modelform.cleaned_data['name'], 
                                          password=modelform.cleaned_data['password'] if modelform.cleaned_data['password'].strip() else None, 
                                          slug=slugify( modelform.cleaned_data['name'] + '-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5)) )
                                          )
            newroom.save()

            if not UserInRoom.objects.filter(user=request.user).exists():
                userinroom = UserInRoom.objects.create(user=request.user, room=newroom, host=True)
                userinroom.save()
            else:
                if not UserInRoom.objects.filter(user=request.user, room=newroom):
                    userinroom = UserInRoom.objects.filter(user=request.user).first()
                    userinroom.delete()
                    userinroom = UserInRoom.objects.create(user=request.user, room=newroom, host=False)
                    userinroom.save()
            
            return redirect('rooms:rooms_joining', slug=newroom.slug)
        return redirect('rooms:rooms')
    
@csrf_exempt
@login_required(login_url='start:home')
def rooms_leave(request):
    userinroom = UserInRoom.objects.filter(user=request.user).first()
    if userinroom:
        userinroom.delete()
    return redirect('rooms:rooms')

# Frontend requests

@csrf_exempt
@login_required(login_url='start:home')
def get_users_in_room(request, slug):
    if request.method == 'GET':        
        room = Room.objects.filter(slug=slug).first()
        if room:
            all_users_in_room = UserInRoom.objects.filter(room=room)
            user_list = [{'username': user.user.username, 'nickname': user.user.first_name, 'host': user.host} for user in all_users_in_room]

            return JsonResponse({'users': user_list})
    return JsonResponse({'error': 'Invalid request'})

@csrf_exempt
@login_required(login_url='start:home')
def get_rooms(request):
    if request.method == 'GET':
        all_rooms = Room.objects.all()
        rooms_list = [{'name': unique_room.name, 
                       'slug': unique_room.slug, 
                       'count': unique_room.userinroom_set.count(),
                       'is_connected': UserInRoom.objects.filter(room=unique_room, user=request.user).exists()
        } for unique_room in all_rooms]

        for room in all_rooms:
            all_users_in_room = UserInRoom.objects.filter(room=room)
            if all_users_in_room:
                    host = False
                    for host_search in [user.host for user in all_users_in_room]:
                        if host_search == True:
                            host = True
                            break
                    if not host:
                        room.delete()
                    host = False
            else:
                room.delete()

        

        return JsonResponse({'rooms': rooms_list})
    return JsonResponse({'error': 'Invalid request'})
