from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.views import View
from django.views.generic import RedirectView

from .models import *

from .forms import *


# АВТЕНТИФІКАЦІЯ

class RegisterView(View):
    form_class = RegisterForm
    template_name = 'auth/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('feed')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('feed')

        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')

        return render(request, self.template_name, {'form': form})


class LoginView(View):
    form_class = LoginForm
    template_name = 'auth/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('feed')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('feed')

        form = self.form_class(request.POST)
        if form.is_valid():
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

        return render(request, self.template_name, {'form': form})


class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        logout(request)
        return redirect('login')

    def get(self, request):
        return redirect('feed')


# ПРОФІЛЬ

class ProfileView(View):
    def get(self, request, username):
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


class ProfileEditView(LoginRequiredMixin, View):
    form_class = ProfileEditForm
    template_name = 'profile/edit.html'

    def get(self, request, username):
        if request.user.username != username:
            return redirect('profile', username=request.user.username)

        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, username):
        if request.user.username != username:
            return redirect('profile', username=request.user.username)

        form = self.form_class(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('profile', username=username)

        return render(request, self.template_name, {'form': form})


class ProfileFriendsView(View):
    def get(self, request, username):
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


class ProfileFollowersView(View):
    def get(self, request, username):
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


class ProfileFollowingView(View):
    def get(self, request, username):
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


# ------------------
class FeedView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse('Вітаємо, {}! Стрічка буде тут.'.format(request.user.username))


# ЗАГЛУШКИ

class FriendsView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse('TODO: список друзів')


class FriendRequestSendView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs['user_id'])
        return reverse('profile', kwargs={'username': user.username})


class FriendRemoveView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs['user_id'])
        return reverse('profile', kwargs={'username': user.username})


class SubscribeView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs['user_id'])
        return reverse('profile', kwargs={'username': user.username})


class UnsubscribeView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs['user_id'])
        return reverse('profile', kwargs={'username': user.username})


class GroupListView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse('TODO: групи')


class ChatListView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse('TODO: чат')


class NotificationsView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse('TODO: сповіщення')