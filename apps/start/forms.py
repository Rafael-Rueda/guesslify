from django import forms

class NicknameForm(forms.Form):
    nickname = forms.CharField(required=True, label="Enter your nickname: ", widget=forms.TextInput(), max_length=20)

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')

        if len(nickname) < 3:
            raise forms.ValidationError("Your nickname must have at least 3 characters.")

        return nickname
