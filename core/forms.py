from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Recording

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES[:2])

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

class RecordingForm(forms.ModelForm):
    class Meta:
        model = Recording
        fields = ['title', 'language', 'audio']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Bhojpuri folk story'}),
            'language': forms.Select(choices=[(x, x) for x in ['Bhojpuri', 'Awadhi', 'Maithili', 'Hindi', 'Bundeli', 'Other']]),
            'audio': forms.FileInput(attrs={'accept': 'audio/*'}),
        }

    def clean_audio(self):
        file = self.cleaned_data['audio']
        if file.size > 10 * 1024 * 1024:
            raise forms.ValidationError('Audio must be 10 MB or smaller.')
        import os
        if os.path.splitext(file.name)[1].lower() not in {'.mp3', '.wav', '.webm', '.ogg', '.m4a'}:
            raise forms.ValidationError('Please use MP3, WAV, WebM, OGG or M4A audio.')
        return file

class ConsentForm(forms.ModelForm):
    class Meta:
        model = Recording
        fields = ['allow_research','allow_education','allow_ai','allow_commercial']
        labels = {'allow_research':'Allow academic research','allow_education':'Allow education','allow_ai':'Allow AI training','allow_commercial':'Allow commercial use'}
