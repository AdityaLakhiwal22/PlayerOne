from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import GamePost, JoinRequest, Comment, PlayerProfile, Venue


BS = {'class': 'form-control'}
BS_SELECT = {'class': 'form-select'}


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs=BS))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update(BS_SELECT)
            else:
                field.widget.attrs.update(BS)


class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = PlayerProfile
        fields = ['bio', 'city', 'area', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={**BS, 'rows': 3, 'placeholder': 'Tell others about yourself...'}),
            'city': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. Mumbai'}),
            'area': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. Andheri West'}),
            'avatar': forms.FileInput(attrs=BS),
        }


class GamePostForm(forms.ModelForm):
    class Meta:
        model = GamePost
        fields = [
            'mode', 'sport', 'title', 'description',
            'players_have', 'players_needed', 'skill_level',
            'location', 'city', 'play_date', 'play_time',
            'game_platform', 'game_id', 'map_link', 'whatsapp_link',
        ]
        widgets = {
            'mode': forms.Select(attrs=BS_SELECT),
            'sport': forms.Select(attrs=BS_SELECT),
            'skill_level': forms.Select(attrs=BS_SELECT),
            'title': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. Need 4 players for cricket at Azad Maidan'}),
            'description': forms.Textarea(attrs={**BS, 'rows': 3, 'placeholder': 'Extra details...'}),
            'players_have': forms.NumberInput(attrs=BS),
            'players_needed': forms.NumberInput(attrs=BS),
            'play_date': forms.DateInput(attrs={**BS, 'type': 'date'}),
            'play_time': forms.TimeInput(attrs={**BS, 'type': 'time'}),
            'location': forms.TextInput(attrs={**BS, 'placeholder': 'Ground/Venue name'}),
            'city': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. Mumbai'}),
            'game_platform': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. Mobile, PC'}),
            'game_id': forms.TextInput(attrs={**BS, 'placeholder': 'Your in-game ID'}),
            'map_link': forms.URLInput(attrs={**BS, 'placeholder': 'https://maps.google.com/...'}),
            'whatsapp_link': forms.URLInput(attrs={**BS, 'placeholder': 'https://chat.whatsapp.com/...'}),
        }


class JoinRequestForm(forms.ModelForm):
    class Meta:
        model = JoinRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={**BS, 'rows': 2, 'placeholder': 'Why do you want to join?'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={**BS, 'placeholder': 'Add a comment...'}),
        }

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = [
            'name', 'venue_type', 'area', 'city', 'address',
            'map_link', 'sports', 'contact', 'opening_hours',
            'entry_fee', 'price_per_hour', 'description',
            'image1', 'image2', 'image3',
            'latitude', 'longitude',
        ]
        widgets = {
            'name': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. Azad Ground'}),
            'venue_type': forms.Select(attrs=BS_SELECT),
            'area': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. Vile Parle'}),
            'city': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. Mumbai'}),
            'address': forms.Textarea(attrs={**BS, 'rows': 2, 'placeholder': 'Full address...'}),
            'map_link': forms.URLInput(attrs={**BS, 'placeholder': 'https://maps.google.com/...'}),
            'sports': forms.Select(attrs=BS_SELECT),
            'contact': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. 9876543210'}),
            'opening_hours': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. 6am - 10pm'}),
            'entry_fee': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. Free, Rs 50/person'}),
            'price_per_hour': forms.TextInput(attrs={**BS, 'placeholder': 'e.g. Rs 800/hr'}),
            'description': forms.Textarea(attrs={**BS, 'rows': 3, 'placeholder': 'Any extra info...'}),
            'latitude': forms.NumberInput(attrs={**BS, 'placeholder': 'e.g. 19.1075'}),
            'longitude': forms.NumberInput(attrs={**BS, 'placeholder': 'e.g. 72.8263'}),
            'image1': forms.FileInput(attrs=BS),
            'image2': forms.FileInput(attrs=BS),
            'image3': forms.FileInput(attrs=BS),
        }