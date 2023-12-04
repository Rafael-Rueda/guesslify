from django.urls import path

from apps.rooms import views

app_name = 'rooms'

urlpatterns = [
    path('rooms-checkin/', views.rooms_checkin, name='rooms_checkin'),
    path('rooms/', views.rooms, name='rooms'),
    path('rooms/create/create-room/', views.rooms_create, name='rooms_create'),
    path('rooms/leave/leave-room/', views.rooms_leave, name='rooms_leave'),
    path('rooms/<slug:slug>/', views.rooms_joining, name='rooms_joining'),
    
    # frontend requests
    path('rooms/get-users/<slug:slug>', views.get_users_in_room, name='get_users_in_room'),
    path('rooms/request/get-rooms/', views.get_rooms, name='get_rooms')
]
