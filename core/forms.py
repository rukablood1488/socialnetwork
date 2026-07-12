from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import *


class RegisterForm(forms.Form):
    username = forms.CharField(
        label='Імʼя користувача',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'john_doe'}),
    )
    email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'john@example.com'}),
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
    )
    password2 = forms.CharField(
        label='Повторіть пароль',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Це імʼя вже зайнято.')
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Паролі не збігаються.')
        return cleaned

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data.get('email', ''),
            password=data['password1'],
        )
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Імʼя користувача',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'john_doe'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
    )


class ProfileEditForm(forms.Form):
    first_name = forms.CharField(
        label='Імʼя',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Іван'}),
    )
    last_name = forms.CharField(
        label='Прізвище',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Петренко'}),
    )
    email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'ivan@example.com'}),
    )
 
    bio = forms.CharField(
        label='Біографія',
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Розкажіть про себе...'}),
    )
    birth_date = forms.DateField(
        label='Дата народження',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    avatar = forms.ImageField(
        label='Аватар',
        required=False,
    )
    cover = forms.ImageField(
        label='Обкладинка',
        required=False,
    )
 
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            profile = getattr(user, 'profile', None)
            if profile:
                self.fields['bio'].initial = profile.bio
                self.fields['birth_date'].initial = profile.birth_date
 
    def save(self, user):
        data = self.cleaned_data
 
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.email = data.get('email', '')
        user.save()
 
        profile = user.profile
        profile.bio = data.get('bio', '')
        profile.birth_date = data.get('birth_date') or None
        if data.get('avatar'):
            profile.avatar = data['avatar']
        if data.get('cover'):
            profile.cover = data['cover']
        profile.save()
 
        return user
    

class PostForm(forms.ModelForm):
    class Meta:
        model  = Post
        fields = ['text', 'content_type', 'image', 'video', 'link']
        labels = {
            'text': 'Текст',
            'content_type': 'Тип контенту',
            'image': 'Зображення',
            'video': 'Відео',
            'link': 'Посилання',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Що у вас нового?',
            }),
            'link': forms.URLInput(attrs={
                'placeholder': 'https://...',
            }),
            'content_type': forms.Select(),
        }
 
    def clean(self):
        cleaned = super().clean()
        content_type = cleaned.get('content_type')
        if content_type == Post.ContentType.IMAGE and not cleaned.get('image'):
            self.add_error('image', 'Додайте зображення для цього типу контенту.')
        if content_type == Post.ContentType.VIDEO and not cleaned.get('video'):
            self.add_error('video', 'Додайте відео для цього типу контенту.')
        if content_type == Post.ContentType.LINK and not cleaned.get('link'):
            self.add_error('link', 'Вкажіть посилання для цього типу контенту.')
        return cleaned
 
 
 
class CommentForm(forms.ModelForm):
    class Meta:
        model  = Comment
        fields = ['text']
        labels = {'text': ''}
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Написати коментар...',
            }),
        }