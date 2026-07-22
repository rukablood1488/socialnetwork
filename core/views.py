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


# ПОСТИ
 
class PostCreateView(LoginRequiredMixin, View):
    template_name = 'posts/create.html'
 
    def get(self, request):
        form = PostForm()
        return render(request, self.template_name, {'form': form})
 
    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
        return render(request, self.template_name, {'form': form})
 
 
class PostDetailView(View):
    template_name = 'posts/detail.html'
 
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        comments = post.comments.filter(
            parent__isnull=True,
        ).select_related('author').prefetch_related('replies__author')
        comment_form = CommentForm()
 
        user_liked    = False
        user_reposted = False
        if request.user.is_authenticated:
            user_liked    = post.likes.filter(user=request.user).exists()
            user_reposted = post.reposts.filter(user=request.user).exists()
 
        return render(request, self.template_name, {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
            'likes_count': post.likes.count(),
            'repost_count': post.reposts.count(),
            'user_liked': user_liked,
            'user_reposted': user_reposted,
        })
 
 
class PostEditView(LoginRequiredMixin, View):
    template_name = 'posts/edit.html'
 
    def get_post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user and not request.user.is_staff:
            return None, redirect('post_detail', pk=pk)
        return post, None
 
    def get(self, request, pk):
        post, error = self.get_post(request, pk)
        if error:
            return error
        form = PostForm(instance=post)
        return render(request, self.template_name, {'form': form, 'post': post})
 
    def post(self, request, pk):
        post, error = self.get_post(request, pk)
        if error:
            return error
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
        return render(request, self.template_name, {'form': form, 'post': post})
 
 
class PostDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.author == request.user or request.user.is_staff:
            post.delete()
        return redirect('feed')
 
 
class PostLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
        return redirect('post_detail', pk=pk)
 
 
class PostRepostView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user:
            Repost.objects.get_or_create(user=request.user, post=post)
        return redirect('post_detail', pk=pk)
 
 
class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, pk=parent_id)
            comment.save()
        return redirect('post_detail', pk=pk)
 
 
class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        if comment.author == request.user or request.user.is_staff:
            post_pk = comment.post_id
            comment.delete()
            return redirect('post_detail', pk=post_pk)
        return redirect('feed')


# ------------------
class FeedView(LoginRequiredMixin, View):
    template_name = 'feed/index.html'

    def get(self, request):
        friendships = Friendship.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user),
            status=Friendship.Status.ACCEPTED,
        ).values_list('sender_id', 'receiver_id')
        friend_ids = {uid for pair in friendships for uid in pair} - {request.user.id}

        following_ids = set(
            Subscription.objects.filter(
                follower=request.user,
            ).values_list('following_id', flat=True)
        )

        author_ids = friend_ids | following_ids | {request.user.id}
        posts = Post.objects.filter(
            author_id__in=author_ids,
            group__isnull=True,
        ).select_related(
            'author',
            'author__profile',
        ).prefetch_related(
            'likes',
            'reposts',
            'comments',
        ).order_by('-created_at')

 
        liked_ids = set(request.user.likes.values_list('post_id', flat=True))
        reposted_ids = set(request.user.reposts.values_list('post_id', flat=True))

        return render(request, self.template_name, {
            'posts': posts,
            'liked_ids': liked_ids,
            'reposted_ids': reposted_ids,
        })


# ДРУЗІ ТА ПІДПИСКИ

class FriendsView(LoginRequiredMixin, View):
    template_name = 'friends/list.html'

    def get(self, request):
        friendships = Friendship.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user),
            status=Friendship.Status.ACCEPTED,
        ).select_related('sender', 'receiver')

        friends = [
            f.receiver if f.sender == request.user else f.sender
            for f in friendships
        ]
        return render(request, self.template_name, {'friends': friends})


class FriendRequestsView(LoginRequiredMixin, View):
    template_name = 'friends/requests.html'

    def get(self, request):
        pending = Friendship.objects.filter(
            receiver=request.user,
            status=Friendship.Status.PENDING,
        ).select_related('sender', 'sender__profile')
        return render(request, self.template_name, {'pending': pending})


class FriendRequestSendView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        if target != request.user:
            already_exists = Friendship.objects.filter(
                Q(sender=request.user, receiver=target) |
                Q(sender=target, receiver=request.user),
            ).exists()
            if not already_exists:
                Friendship.objects.create(
                    sender=request.user,
                    receiver=target,
                    status=Friendship.Status.PENDING,
                )
        return redirect('profile', username=target.username)

    def get(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        return redirect('profile', username=target.username)


class FriendRequestAcceptView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        friendship = get_object_or_404(
            Friendship,
            pk=request_id,
            receiver=request.user,
            status=Friendship.Status.PENDING,
        )
        friendship.status = Friendship.Status.ACCEPTED
        friendship.save()
        return redirect('friend_requests')

    def get(self, request, request_id):
        return redirect('friend_requests')


class FriendRequestDeclineView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        friendship = get_object_or_404(
            Friendship,
            pk=request_id,
            receiver=request.user,
            status=Friendship.Status.PENDING,
        )
        friendship.delete()
        return redirect('friend_requests')

    def get(self, request, request_id):
        return redirect('friend_requests')


class FriendRemoveView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        Friendship.objects.filter(
            Q(sender=request.user, receiver=target) |
            Q(sender=target, receiver=request.user),
            status=Friendship.Status.ACCEPTED,
        ).delete()
        return redirect('profile', username=target.username)

    def get(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        return redirect('profile', username=target.username)


class SubscribeView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        if target != request.user:
            Subscription.objects.get_or_create(
                follower=request.user,
                following=target,
            )
        return redirect('profile', username=target.username)

    def get(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        return redirect('profile', username=target.username)


class UnsubscribeView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        Subscription.objects.filter(
            follower=request.user,
            following=target,
        ).delete()
        return redirect('profile', username=target.username)

    def get(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        return redirect('profile', username=target.username)
    


# ЗАГЛУШКИ

class GroupListView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse('TODO: групи')


class ChatListView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse('TODO: чат')


class NotificationsView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse('TODO: сповіщення')