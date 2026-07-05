from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse

from .models import *

from .forms import RegisterForm, LoginForm
 
 
# АВТЕНТИФІКАЦІЯ
 
def register(request):
    if request.user.is_authenticated:
        return redirect('feed')
 
    form = RegisterForm(request.POST or None)
 
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('feed')
 
    return render(request, 'auth/register.html', {'form': form})
 
 
def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
 
    form = LoginForm(request.POST or None)
 
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'feed')
            return redirect(next_url)
        else:
            form.add_error(None, 'Невірний логін або пароль.')
 
    return render(request, 'auth/login.html', {'form': form})
 
 
@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('feed')


#------------------
@login_required
def feed(request):
    return HttpResponse('Вітаємо, {}! Стрічка буде тут.'.format(request.user.username))