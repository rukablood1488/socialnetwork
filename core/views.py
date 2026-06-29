from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q

from .models import *



# СТРІЧКА

@login_required
def feed(request):
    friend_ids = Friendship.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status=Friendship.Status.ACCEPTED,
    ).values_list('sender_id', 'receiver_id')
    friend_ids = {uid for pair in friend_ids for uid in pair} - {request.user.id}

    following_ids = Subscription.objects.filter(
        follower=request.user,
    ).values_list('following_id', flat=True)

    author_ids = friend_ids | set(following_ids) | {request.user.id}
    posts = Post.objects.filter(
        author_id__in=author_ids,
        group__isnull=True,
    ).select_related('author', 'author__profile').order_by('-created_at')

    return render(request, 'feed/index.html', {'posts': posts})



# АВТЕНТИФІКАЦІЯ

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = {}
        if not username:
            errors['username'] = 'Введіть імʼя користувача'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Це імʼя вже зайнято'
        if password1 != password2:
            errors['password2'] = 'Паролі не збігаються'
        if len(password1) < 8:
            errors['password1'] = 'Пароль має бути не менше 8 символів'

        if not errors:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
            )
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('feed')

        return render(request, 'auth/register.html', {
            'errors': errors,
            'old': request.POST,
        })

    return render(request, 'auth/register.html', {})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'feed')
            return redirect(next_url)

        return render(request, 'auth/login.html', {
            'error': 'Невірний логін або пароль',
            'old': request.POST,
        })

    return render(request, 'auth/login.html', {})


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')



# ПРОФІЛЬ

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=profile_user,
        group__isnull=True,
    ).order_by('-created_at')

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

    friends_count = Friendship.objects.filter(
        Q(sender=profile_user) | Q(receiver=profile_user),
        status=Friendship.Status.ACCEPTED,
    ).count()
    followers_count = Subscription.objects.filter(following=profile_user).count()
    following_count = Subscription.objects.filter(follower=profile_user).count()

    return render(request, 'profile/detail.html', {
        'profile_user': profile_user,
        'posts': posts,
        'is_friend': is_friend,
        'is_pending': is_pending,
        'is_following': is_following,
        'friends_count': friends_count,
        'followers_count': followers_count,
        'following_count': following_count,
    })


@login_required
def profile_edit(request, username):
    if request.user.username != username:
        return redirect('profile', username=request.user.username)

    profile_obj = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        profile_obj.bio = request.POST.get('bio', '').strip()
        profile_obj.birth_date = request.POST.get('birth_date') or None
        if 'avatar' in request.FILES:
            profile_obj.avatar = request.FILES['avatar']
        if 'cover' in request.FILES:
            profile_obj.cover = request.FILES['cover']
        profile_obj.save()

        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        request.user.save()

        return redirect('profile', username=username)

    return render(request, 'profile/edit.html', {'profile_obj': profile_obj})


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
    subscriptions = Subscription.objects.filter(
        following=profile_user,
    ).select_related('follower')
    followers = [s.follower for s in subscriptions]
    return render(request, 'profile/followers.html', {
        'profile_user': profile_user,
        'followers': followers,
    })


def profile_following(request, username):
    profile_user = get_object_or_404(User, username=username)
    subscriptions = Subscription.objects.filter(
        follower=profile_user,
    ).select_related('following')
    following = [s.following for s in subscriptions]
    return render(request, 'profile/following.html', {
        'profile_user': profile_user,
        'following': following,
    })



# ПОСТИ

@login_required
def post_create(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        link = request.POST.get('link', '').strip()
        content_type = request.POST.get('content_type', Post.ContentType.TEXT)
        group_id = request.POST.get('group_id') or None

        post = Post(
            author=request.user,
            text=text,
            link=link,
            content_type=content_type,
            group_id=group_id,
        )
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        if 'video' in request.FILES:
            post.video = request.FILES['video']
        post.save()
        return redirect('post_detail', pk=post.pk)

    groups = GroupMembership.objects.filter(
        user=request.user,
    ).select_related('group')
    return render(request, 'posts/create.html', {'groups': groups})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(
        post=post,
        parent__isnull=True,
    ).select_related('author').prefetch_related('replies__author')
    likes_count = post.likes.count()
    repost_count = post.reposts.count()

    user_liked = False
    user_reposted = False
    if request.user.is_authenticated:
        user_liked = post.likes.filter(user=request.user).exists()
        user_reposted = post.reposts.filter(user=request.user).exists()

    return render(request, 'posts/detail.html', {
        'post': post,
        'comments': comments,
        'likes_count': likes_count,
        'repost_count': repost_count,
        'user_liked': user_liked,
        'user_reposted': user_reposted,
    })


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)

    if request.method == 'POST':
        post.text = request.POST.get('text', '').strip()
        post.link = request.POST.get('link', '').strip()
        post.content_type = request.POST.get('content_type', post.content_type)
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        if 'video' in request.FILES:
            post.video = request.FILES['video']
        post.save()
        return redirect('post_detail', pk=post.pk)

    return render(request, 'posts/edit.html', {'post': post})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
    return redirect('feed')


@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return redirect('post_detail', pk=pk)


@login_required
def post_repost(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        Repost.objects.get_or_create(user=request.user, post=post)
    return redirect('post_detail', pk=pk)


@login_required
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        parent_id = request.POST.get('parent_id') or None
        if text:
            Comment.objects.create(
                post=post,
                author=request.user,
                text=text,
                parent_id=parent_id,
            )
    return redirect('post_detail', pk=pk)


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post_pk = comment.post_id
    if request.method == 'POST':
        comment.delete()
    return redirect('post_detail', pk=post_pk)



# ДРУЗІ ТА ПІДПИСКИ

@login_required
def friends(request):
    friendships = Friendship.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status=Friendship.Status.ACCEPTED,
    ).select_related('sender', 'receiver')

    friends_list = [
        f.receiver if f.sender == request.user else f.sender
        for f in friendships
    ]
    return render(request, 'friends/list.html', {'friends': friends_list})


@login_required
def friend_requests(request):
    pending = Friendship.objects.filter(
        receiver=request.user,
        status=Friendship.Status.PENDING,
    ).select_related('sender')
    return render(request, 'friends/requests.html', {'pending': pending})


@login_required
def friend_request_send(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target != request.user:
        Friendship.objects.get_or_create(
            sender=request.user,
            receiver=target,
            defaults={'status': Friendship.Status.PENDING},
        )
    return redirect('profile', username=target.username)


@login_required
def friend_request_accept(request, request_id):
    friendship = get_object_or_404(
        Friendship,
        pk=request_id,
        receiver=request.user,
        status=Friendship.Status.PENDING,
    )
    if request.method == 'POST':
        friendship.status = Friendship.Status.ACCEPTED
        friendship.save()
    return redirect('friend_requests')


@login_required
def friend_request_decline(request, request_id):
    friendship = get_object_or_404(
        Friendship,
        pk=request_id,
        receiver=request.user,
        status=Friendship.Status.PENDING,
    )
    if request.method == 'POST':
        friendship.delete()
    return redirect('friend_requests')


@login_required
def friend_remove(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        Friendship.objects.filter(
            Q(sender=request.user, receiver=target) |
            Q(sender=target, receiver=request.user),
            status=Friendship.Status.ACCEPTED,
        ).delete()
    return redirect('profile', username=target.username)


@login_required
def subscribe(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target != request.user:
        Subscription.objects.get_or_create(
            follower=request.user,
            following=target,
        )
    return redirect('profile', username=target.username)


@login_required
def unsubscribe(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    Subscription.objects.filter(
        follower=request.user,
        following=target,
    ).delete()
    return redirect('profile', username=target.username)



# ГРУПИ

def group_list(request):
    groups = Group.objects.all().order_by('name')
    return render(request, 'groups/list.html', {'groups': groups})


@login_required
def group_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if name:
            group = Group.objects.create(
                name=name,
                description=description,
                creator=request.user,
            )
            if 'cover' in request.FILES:
                group.cover = request.FILES['cover']
                group.save()
            GroupMembership.objects.create(
                group=group,
                user=request.user,
                role=GroupMembership.Role.ADMIN,
            )
            return redirect('group_detail', pk=group.pk)

    return render(request, 'groups/create.html', {})


def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    posts = Post.objects.filter(group=group).select_related(
        'author', 'author__profile',
    ).order_by('-created_at')

    is_member = is_admin = False
    if request.user.is_authenticated:
        membership = GroupMembership.objects.filter(
            group=group, user=request.user,
        ).first()
        is_member = membership is not None
        is_admin = membership.role == GroupMembership.Role.ADMIN if membership else False

    members_count = group.memberships.count()

    return render(request, 'groups/detail.html', {
        'group': group,
        'posts': posts,
        'is_member': is_member,
        'is_admin': is_admin,
        'members_count': members_count,
    })


@login_required
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    get_object_or_404(
        GroupMembership,
        group=group,
        user=request.user,
        role=GroupMembership.Role.ADMIN,
    )

    if request.method == 'POST':
        group.name = request.POST.get('name', group.name).strip()
        group.description = request.POST.get('description', '').strip()
        if 'cover' in request.FILES:
            group.cover = request.FILES['cover']
        group.save()
        return redirect('group_detail', pk=pk)

    return render(request, 'groups/edit.html', {'group': group})


@login_required
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk, creator=request.user)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list')
    return redirect('group_detail', pk=pk)


@login_required
def group_join(request, pk):
    group = get_object_or_404(Group, pk=pk)
    GroupMembership.objects.get_or_create(
        group=group,
        user=request.user,
        defaults={'role': GroupMembership.Role.MEMBER},
    )
    return redirect('group_detail', pk=pk)


@login_required
def group_leave(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST' and group.creator != request.user:
        GroupMembership.objects.filter(
            group=group,
            user=request.user,
        ).delete()
    return redirect('group_detail', pk=pk)


def group_members(request, pk):
    group = get_object_or_404(Group, pk=pk)
    memberships = GroupMembership.objects.filter(
        group=group,
    ).select_related('user').order_by('role', 'joined_at')

    is_admin = False
    if request.user.is_authenticated:
        is_admin = memberships.filter(
            user=request.user,
            role=GroupMembership.Role.ADMIN,
        ).exists()

    return render(request, 'groups/members.html', {
        'group': group,
        'memberships': memberships,
        'is_admin': is_admin,
    })


@login_required
def group_kick(request, pk, user_id):
    group = get_object_or_404(Group, pk=pk)
    get_object_or_404(
        GroupMembership,
        group=group,
        user=request.user,
        role=GroupMembership.Role.ADMIN,
    )
    target = get_object_or_404(User, pk=user_id)
    if request.method == 'POST' and target != group.creator:
        GroupMembership.objects.filter(group=group, user=target).delete()
    return redirect('group_members', pk=pk)


@login_required
def group_promote(request, pk, user_id):
    group = get_object_or_404(Group, pk=pk, creator=request.user)
    target = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        GroupMembership.objects.filter(
            group=group,
            user=target,
        ).update(role=GroupMembership.Role.ADMIN)
    return redirect('group_members', pk=pk)



# ЧАТ

@login_required
def chat_list(request):
    chats = Chat.objects.filter(
        participants=request.user,
    ).prefetch_related('participants', 'messages').order_by('-created_at')
    return render(request, 'chat/list.html', {'chats': chats})


@login_required
def chat_create_private(request, user_id):
    target = get_object_or_404(User, pk=user_id)

    existing = Chat.objects.filter(
        is_group=False,
        participants=request.user,
    ).filter(
        participants=target,
    ).first()

    if existing:
        return redirect('chat_detail', pk=existing.pk)

    chat = Chat.objects.create(is_group=False)
    chat.participants.add(request.user, target)
    return redirect('chat_detail', pk=chat.pk)


@login_required
def chat_create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        user_ids = request.POST.getlist('participants')
        participants = User.objects.filter(pk__in=user_ids)

        chat = Chat.objects.create(name=name, is_group=True)
        chat.participants.add(request.user, *participants)
        return redirect('chat_detail', pk=chat.pk)

    friends_qs = Friendship.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status=Friendship.Status.ACCEPTED,
    ).select_related('sender', 'receiver')
    friends = [
        f.receiver if f.sender == request.user else f.sender
        for f in friends_qs
    ]
    return render(request, 'chat/create_group.html', {'friends': friends})


@login_required
def chat_detail(request, pk):
    chat = get_object_or_404(Chat, pk=pk, participants=request.user)
    messages = chat.messages.select_related('sender').order_by('created_at')

    messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)

    return render(request, 'chat/detail.html', {
        'chat': chat,
        'messages': messages,
    })


@login_required
def message_send(request, pk):
    chat = get_object_or_404(Chat, pk=pk, participants=request.user)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        msg = Message(chat=chat, sender=request.user, text=text)
        if 'image' in request.FILES:
            msg.image = request.FILES['image']
        if 'video' in request.FILES:
            msg.video = request.FILES['video']
        if 'file' in request.FILES:
            msg.file = request.FILES['file']
        if text or msg.image or msg.video or msg.file:
            msg.save()
    return redirect('chat_detail', pk=pk)


@login_required
def message_delete(request, pk, msg_id):
    message = get_object_or_404(Message, pk=msg_id, sender=request.user, chat_id=pk)
    if request.method == 'POST':
        message.delete()
    return redirect('chat_detail', pk=pk)


@login_required
def chat_mark_read(request, pk):
    chat = get_object_or_404(Chat, pk=pk, participants=request.user)
    chat.messages.exclude(sender=request.user).update(is_read=True)
    return redirect('chat_detail', pk=pk)



# СПОВІЩЕННЯ

@login_required
def notifications(request):
    notifs = Notification.objects.filter(
        recipient=request.user,
    ).select_related('sender', 'post').order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifs})


@login_required
def notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if request.method == 'POST':
        notif.is_read = True
        notif.save()
    return redirect('notifications')


@login_required
def notifications_read_all(request):
    if request.method == 'POST':
        Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True)
    return redirect('notifications')