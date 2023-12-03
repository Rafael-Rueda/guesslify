from django import forms
from apps.rooms import models

class CreateRoomForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, label='Password (optional)')
    class Meta:
        model = models.Room
        fields = ('name',)

class JoinPasswordRoomForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), required=True, label='Password')