from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.views import View

from .models import *

from .forms import *


def get_friend_ids(user):

    following_ids = set(
        Subscription.objects.filter(follower=user).values_list('following_id', flat=True)
    )
    follower_ids = set(
        Subscription.objects.filter(following=user).values_list('follower_id', flat=True)
    )
    return following_ids & follower_ids


def can_view_user_content(viewer, target_user):
    profile = getattr(target_user, 'profile', None)
    if not profile or not profile.is_private:
        return True
 
    if not viewer.is_authenticated:
        return False
 
    if viewer == target_user or viewer.is_staff:
        return True
 
    return Subscription.objects.filter(
        follower=viewer,
        following=target_user,
        status=Subscription.Status.ACCEPTED,
    ).exists()


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
 
        can_view = can_view_user_content(request.user, profile_user)
 
        friends_count = len(get_friend_ids(profile_user))
        followers_count = Subscription.objects.filter(
            following=profile_user, status=Subscription.Status.ACCEPTED,
        ).count()
        following_count = Subscription.objects.filter(
            follower=profile_user, status=Subscription.Status.ACCEPTED,
        ).count()
 
        if can_view:
            posts = profile_user.posts.filter(group__isnull=True).order_by('-created_at')
        else:
            posts = Post.objects.none()
 
        is_friend = is_following = is_pending = False
        if request.user.is_authenticated and request.user != profile_user:
            is_following = Subscription.objects.filter(
                follower=request.user,
                following=profile_user,
                status=Subscription.Status.ACCEPTED,
            ).exists()
            is_pending = Subscription.objects.filter(
                follower=request.user,
                following=profile_user,
                status=Subscription.Status.PENDING,
            ).exists()
            is_followed_back = Subscription.objects.filter(
                follower=profile_user,
                following=request.user,
                status=Subscription.Status.ACCEPTED,
            ).exists()
            is_friend = is_following and is_followed_back
 
        return render(request, 'profile/detail.html', {
            'profile_user': profile_user,
            'posts': posts,
            'friends_count': friends_count,
            'followers_count': followers_count,
            'following_count': following_count,
            'is_friend': is_friend,
            'is_following': is_following,
            'is_pending': is_pending,
            'is_locked': not can_view,
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
 
        if not can_view_user_content(request.user, profile_user):
            messages.info(request, 'Цей акаунт приватний. Підпишіться, щоб побачити цю інформацію.')
            return redirect('profile', username=username)
 
        friend_ids = get_friend_ids(profile_user)
        friends = User.objects.filter(pk__in=friend_ids).select_related('profile')
 
        return render(request, 'profile/friends.html', {
            'profile_user': profile_user,
            'friends': friends,
        })
 
 
class ProfileFollowersView(View):
    def get(self, request, username):
        profile_user = get_object_or_404(User, username=username)
 
        if not can_view_user_content(request.user, profile_user):
            messages.info(request, 'Цей акаунт приватний. Підпишіться, щоб побачити цю інформацію.')
            return redirect('profile', username=username)
 
        followers = [
            s.follower for s in
            Subscription.objects.filter(
                following=profile_user, status=Subscription.Status.ACCEPTED,
            ).select_related('follower')
        ]
        return render(request, 'profile/followers.html', {
            'profile_user': profile_user,
            'followers': followers,
        })
 
 
class ProfileFollowingView(View):
    def get(self, request, username):
        profile_user = get_object_or_404(User, username=username)
 
        if not can_view_user_content(request.user, profile_user):
            messages.info(request, 'Цей акаунт приватний. Підпишіться, щоб побачити цю інформацію.')
            return redirect('profile', username=username)
 
        following = [
            s.following for s in
            Subscription.objects.filter(
                follower=profile_user, status=Subscription.Status.ACCEPTED,
            ).select_related('following')
        ]
        return render(request, 'profile/following.html', {
            'profile_user': profile_user,
            'following': following,
        })


# ПОСТИ
 
class PostCreateView(LoginRequiredMixin, View):
    template_name = 'posts/create.html'
 
    def get_group(self, request, group_id):
        if not group_id:
            return None, None
        group = get_object_or_404(Group, pk=group_id)
        is_member = GroupMembership.objects.filter(group=group, user=request.user).exists()
        if not is_member:
            return None, redirect('group_detail', pk=group_id)
        return group, None
 
    def get(self, request):
        group, error = self.get_group(request, request.GET.get('group'))
        if error:
            return error
        form = PostForm()
        return render(request, self.template_name, {'form': form, 'group': group})
 
    def post(self, request):
        group, error = self.get_group(request, request.POST.get('group_id'))
        if error:
            return error
 
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.group = group
            post.save()
            if group:
                return redirect('group_detail', pk=group.pk)
            return redirect('post_detail', pk=post.pk)
 
        return render(request, self.template_name, {'form': form, 'group': group})
 
 
class PostDetailView(View):
    template_name = 'posts/detail.html'
 
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        comments = post.comments.filter(
            parent__isnull=True,
        ).select_related('author').prefetch_related('replies__author')
        comment_form = CommentForm()
 
        user_liked = False
        user_reposted = False
        if request.user.is_authenticated:
            user_liked = post.likes.filter(user=request.user).exists()
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
        form = PostCaptionEditForm(instance=post)
        return render(request, self.template_name, {'form': form, 'post': post})
 
    def post(self, request, pk):
        post, error = self.get_post(request, pk)
        if error:
            return error
        form = PostCaptionEditForm(request.POST, instance=post)
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
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer or reverse('post_detail', kwargs={'pk': pk}))
 
 
class PostRepostView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user:
            repost, created = Repost.objects.get_or_create(user=request.user, post=post)
            if not created:
                repost.delete()
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer or reverse('post_detail', kwargs={'pk': pk}))
    
    
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

        posts = Post.objects.filter(
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
        friend_ids = get_friend_ids(request.user)
        friends = User.objects.filter(pk__in=friend_ids).select_related('profile')
        return render(request, self.template_name, {'friends': friends})
 
 
class FriendRemoveView(LoginRequiredMixin, View):
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
 
 
class SubscribeView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)
        if target != request.user:
            target_profile = getattr(target, 'profile', None)
            is_private = target_profile.is_private if target_profile else False
            status = Subscription.Status.PENDING if is_private else Subscription.Status.ACCEPTED
 
            Subscription.objects.get_or_create(
                follower=request.user,
                following=target,
                defaults={'status': status},
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
 
 
class SubscriptionRequestsView(LoginRequiredMixin, View):
    template_name = 'friends/subscription_requests.html'
 
    def get(self, request):
        pending = Subscription.objects.filter(
            following=request.user,
            status=Subscription.Status.PENDING,
        ).select_related('follower', 'follower__profile')
        return render(request, self.template_name, {'pending': pending})
 
 
class SubscriptionAcceptView(LoginRequiredMixin, View):
    def post(self, request, sub_id):
        sub = get_object_or_404(
            Subscription,
            pk=sub_id,
            following=request.user,
            status=Subscription.Status.PENDING,
        )
        sub.status = Subscription.Status.ACCEPTED
        sub.save()
        return redirect('subscription_requests')
 
    def get(self, request, sub_id):
        return redirect('subscription_requests')
 
 
class SubscriptionDeclineView(LoginRequiredMixin, View):
    def post(self, request, sub_id):
        sub = get_object_or_404(
            Subscription,
            pk=sub_id,
            following=request.user,
            status=Subscription.Status.PENDING,
        )
        sub.delete()
        return redirect('subscription_requests')
 
    def get(self, request, sub_id):
        return redirect('subscription_requests')


# ГРУПИ

class GroupListView(LoginRequiredMixin, View):
    template_name = 'groups/list.html'

    def get(self, request):
        groups = Group.objects.select_related('creator').order_by('name')

        member_group_ids = set(
            GroupMembership.objects.filter(
                user=request.user,
            ).values_list('group_id', flat=True)
        )

        return render(request, self.template_name, {
            'groups': groups,
            'member_group_ids': member_group_ids,
        })


class GroupCreateView(LoginRequiredMixin, View):
    form_class = GroupForm
    template_name = 'groups/create.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()

            GroupMembership.objects.create(
                group=group,
                user=request.user,
                role=GroupMembership.Role.ADMIN,
            )
            return redirect('group_detail', pk=group.pk)

        return render(request, self.template_name, {'form': form})


class GroupDetailView(LoginRequiredMixin, View):
    template_name = 'groups/detail.html'

    def get(self, request, pk):
        group = get_object_or_404(Group, pk=pk)

        posts = group.posts.select_related(
            'author',
            'author__profile',
        ).prefetch_related(
            'likes',
            'reposts',
            'comments',
        ).order_by('-created_at')

        membership = GroupMembership.objects.filter(
            group=group,
            user=request.user,
        ).first()

        is_member = membership is not None
        is_admin = membership is not None and membership.role == GroupMembership.Role.ADMIN
        is_creator = group.creator_id == request.user.id

        members_count = group.memberships.count()
        liked_ids = set(request.user.likes.values_list('post_id', flat=True))
        reposted_ids = set(request.user.reposts.values_list('post_id', flat=True))

        return render(request, self.template_name, {
            'group': group,
            'posts': posts,
            'is_member': is_member,
            'is_admin': is_admin,
            'is_creator': is_creator,
            'members_count': members_count,
            'liked_ids': liked_ids,
            'reposted_ids': reposted_ids,
        })


class GroupEditView(LoginRequiredMixin, View):
    form_class = GroupForm
    template_name = 'groups/edit.html'

    def get_group(self, request, pk):
        group = get_object_or_404(Group, pk=pk)

        is_admin = GroupMembership.objects.filter(
            group=group,
            user=request.user,
            role=GroupMembership.Role.ADMIN,
        ).exists()

        if not is_admin:
            return None, redirect('group_detail', pk=pk)
        return group, None

    def get(self, request, pk):
        group, error = self.get_group(request, pk)
        if error:
            return error
        form = self.form_class(instance=group)
        return render(request, self.template_name, {'form': form, 'group': group})

    def post(self, request, pk):
        group, error = self.get_group(request, pk)
        if error:
            return error
        form = self.form_class(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_detail', pk=group.pk)
        return render(request, self.template_name, {'form': form, 'group': group})


class GroupDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)

        if group.creator_id == request.user.id or request.user.is_staff:
            group.delete()
            return redirect('group_list')

        return redirect('group_detail', pk=pk)

    def get(self, request, pk):
        return redirect('group_detail', pk=pk)


class GroupJoinView(LoginRequiredMixin, View):
    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        GroupMembership.objects.get_or_create(
            group=group,
            user=request.user,
            defaults={'role': GroupMembership.Role.MEMBER},
        )
        return redirect('group_detail', pk=pk)

    def get(self, request, pk):
        return redirect('group_detail', pk=pk)


class GroupLeaveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)

        if group.creator_id != request.user.id:
            GroupMembership.objects.filter(group=group, user=request.user).delete()

        return redirect('group_detail', pk=pk)

    def get(self, request, pk):
        return redirect('group_detail', pk=pk)



class GroupMembersView(View):
    template_name = 'groups/members.html'
 
    def get(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        memberships = GroupMembership.objects.filter(
            group=group,
        ).select_related('user', 'user__profile').order_by('role', 'joined_at')
 
        is_admin = is_creator = False
        if request.user.is_authenticated:
            is_admin = GroupMembership.objects.filter(
                group=group,
                user=request.user,
                role=GroupMembership.Role.ADMIN,
            ).exists()
            is_creator = group.creator_id == request.user.id
 
        return render(request, self.template_name, {
            'group': group,
            'memberships': memberships,
            'is_admin': is_admin,
            'is_creator': is_creator,
        })
 
 
class GroupKickView(LoginRequiredMixin, View):
    def post(self, request, pk, user_id):
        group = get_object_or_404(Group, pk=pk)
 
        is_admin = GroupMembership.objects.filter(
            group=group,
            user=request.user,
            role=GroupMembership.Role.ADMIN,
        ).exists()
 
        if is_admin:
            target = get_object_or_404(User, pk=user_id)
            if target.id != group.creator_id:
                GroupMembership.objects.filter(group=group, user=target).delete()
 
        return redirect('group_members', pk=pk)
 
    def get(self, request, pk, user_id):
        return redirect('group_members', pk=pk)
 
 
class GroupPromoteView(LoginRequiredMixin, View):
    def post(self, request, pk, user_id):
        group = get_object_or_404(Group, pk=pk)
 
        if group.creator_id == request.user.id:
            target = get_object_or_404(User, pk=user_id)
            GroupMembership.objects.filter(
                group=group,
                user=target,
            ).update(role=GroupMembership.Role.ADMIN)
 
        return redirect('group_members', pk=pk)
 
    def get(self, request, pk, user_id):
        return redirect('group_members', pk=pk)


