from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse

from .models import *

from .forms import *
 
 
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



# ПРОФІЛЬ
 
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
 
    posts = profile_user.posts.filter(
        group__isnull=True,
    ).order_by('-created_at')
 
    friends_count = Friendship.objects.filter(
        Q(sender=profile_user) | Q(receiver=profile_user),
        status=Friendship.Status.ACCEPTED,
    ).count()
    followers_count = Subscription.objects.filter(following=profile_user).count()
    following_count = Subscription.objects.filter(follower=profile_user).count()
 

    is_friend = is_pending = is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_friend = Friendship.objects.filter(
            Q(sender=request.user, receiver=profile_user) |
            Q(sender=profile_user, receiver=request.user),
            status=Friendship.Status.ACCEPTED,
        ).exists()
        is_pending = Friendship.objects.filter(
            sender=request.user,
            receiver=profile_user,
            status=Friendship.Status.PENDING,
        ).exists()
        is_following = Subscription.objects.filter(
            follower=request.user,
            following=profile_user,
        ).exists()
 
    return render(request, 'profile/detail.html', {
        'profile_user': profile_user,
        'posts': posts,
        'friends_count': friends_count,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_friend': is_friend,
        'is_pending': is_pending,
        'is_following': is_following,
    })
 
 
@login_required
def profile_edit(request, username):
    if request.user.username != username:
        return redirect('profile', username=request.user.username)
 
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        user=request.user,
    )
 
    if request.method == 'POST' and form.is_valid():
        form.save(user=request.user)
        return redirect('profile', username=username)
 
    return render(request, 'profile/edit.html', {'form': form})
 
 
def profile_friends(request, username):
    profile_user = get_object_or_404(User, username=username)
    friendships = Friendship.objects.filter(
        Q(sender=profile_user) | Q(receiver=profile_user),
        status=Friendship.Status.ACCEPTED,
    ).select_related('sender', 'receiver')
 
    friends = [
        f.receiver if f.sender == profile_user else f.sender
        for f in friendships
    ]
    return render(request, 'profile/friends.html', {
        'profile_user': profile_user,
        'friends': friends,
    })
 
 
def profile_followers(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = [
        s.follower for s in
        Subscription.objects.filter(
            following=profile_user,
        ).select_related('follower')
    ]
    return render(request, 'profile/followers.html', {
        'profile_user': profile_user,
        'followers': followers,
    })
 
 
def profile_following(request, username):
    profile_user = get_object_or_404(User, username=username)
    following = [
        s.following for s in
        Subscription.objects.filter(
            follower=profile_user,
        ).select_related('following')
    ]
    return render(request, 'profile/following.html', {
        'profile_user': profile_user,
        'following': following,
    })


#------------------
@login_required
def feed(request):
    return HttpResponse('Вітаємо, {}! Стрічка буде тут.'.format(request.user.username))


# ЗАГЛУШКИ 

 
@login_required
def friends(request):
    return HttpResponse('TODO: список друзів')
 
 
@login_required
def friend_request_send(request, user_id):
    return redirect('profile', username=get_object_or_404(User, pk=user_id).username)
 
 
@login_required
def friend_remove(request, user_id):
    return redirect('profile', username=get_object_or_404(User, pk=user_id).username)
 
 
@login_required
def subscribe(request, user_id):
    return redirect('profile', username=get_object_or_404(User, pk=user_id).username)
 
 
@login_required
def unsubscribe(request, user_id):
    return redirect('profile', username=get_object_or_404(User, pk=user_id).username)
 
 
@login_required
def group_list(request):
    return HttpResponse('TODO: групи')
 
 
@login_required
def chat_list(request):
    return HttpResponse('TODO: чат')
 
 
@login_required
def notifications(request):
    return HttpResponse('TODO: сповіщення')