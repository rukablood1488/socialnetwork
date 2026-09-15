from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .models import Chat, Message, Notification, Post
from .forms import ChatEditForm
from .views import get_friend_ids


def _build_chat_sidebar_data(user, chats=None):
    if chats is None:
        chats = Chat.objects.filter(participants=user)

    chats = chats.prefetch_related(
        'participants', 'participants__profile', 'messages',
    ).distinct()

    chats = sorted(
        chats,
        key=lambda c: c.messages.last().created_at if c.messages.exists() else c.created_at,
        reverse=True,
    )

    chat_data = []
    for chat in chats:
        other_user = None
        if not chat.is_group:
            other_user = chat.participants.exclude(pk=user.pk).first()

        last_message = chat.messages.last()
        unread_count = chat.messages.exclude(sender=user).filter(is_read=False).count()

        chat_data.append({
            'chat': chat,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
        })

    return chat_data


def _split_chats_for_sidebar(user):
    all_chats = Chat.objects.filter(participants=user)

    primary = all_chats.exclude(
        Q(status=Chat.Status.PENDING) & ~Q(creator=user)
    )
    incoming_requests = all_chats.filter(
        status=Chat.Status.PENDING,
    ).exclude(creator=user)

    return primary, incoming_requests


def _pending_flags(chat, user):
    is_incoming_pending = False
    is_pending_awaiting = False
    show_request_composer = False

    if not chat.is_group and chat.status == Chat.Status.PENDING:
        if chat.creator_id == user.id:
            if chat.messages.filter(sender=user).exists():
                is_pending_awaiting = True
            else:
                show_request_composer = True
        else:
            is_incoming_pending = True

    return is_incoming_pending, is_pending_awaiting, show_request_composer


class ChatListView(LoginRequiredMixin, View):
    template_name = 'chat/list.html'

    def get(self, request):
        primary_qs, requests_qs = _split_chats_for_sidebar(request.user)
        chat_data = _build_chat_sidebar_data(request.user, primary_qs)
        request_data = _build_chat_sidebar_data(request.user, requests_qs)

        return render(request, self.template_name, {
            'chat_data': chat_data,
            'request_data': request_data,
            'active_chat': None,
        })


class ChatCreatePrivateView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id)

        if target == request.user:
            return redirect('chat_list')

        existing = Chat.objects.filter(
            is_group=False, participants=request.user,
        ).filter(participants=target).first()

        if existing:
            return redirect('chat_detail', pk=existing.pk)

        is_friend = target.pk in get_friend_ids(request.user)
        status = Chat.Status.ACCEPTED if is_friend else Chat.Status.PENDING

        chat = Chat.objects.create(is_group=False, creator=request.user, status=status)
        chat.participants.add(request.user, target)
        return redirect('chat_detail', pk=chat.pk)

    def get(self, request, user_id):
        return self.post(request, user_id)


class ChatCreateGroupView(LoginRequiredMixin, View):
    template_name = 'chat/create_group.html'

    def get(self, request):
        friend_ids = get_friend_ids(request.user)
        friends = User.objects.filter(pk__in=friend_ids).select_related('profile')
        return render(request, self.template_name, {'friends': friends})

    def post(self, request):
        name = request.POST.get('name', '').strip()

        friend_ids = get_friend_ids(request.user)
        selected_ids = {uid for uid in request.POST.getlist('participants') if uid.isdigit()}
        selected_ids = {int(uid) for uid in selected_ids} & friend_ids

        participants = User.objects.filter(pk__in=selected_ids)

        if not participants.exists():
            friends = User.objects.filter(pk__in=friend_ids).select_related('profile')
            return render(request, self.template_name, {
                'friends': friends,
                'error': 'Оберіть хоча б одного друга.',
            })

        chat = Chat.objects.create(name=name, is_group=True, creator=request.user)
        chat.participants.add(request.user, *participants)
        return redirect('chat_detail', pk=chat.pk)


class ChatInfoView(LoginRequiredMixin, View):
    template_name = 'chat/info.html'

    def get_chat(self, request, pk):
        return get_object_or_404(Chat, pk=pk, participants=request.user, is_group=True)

    def get(self, request, pk):
        chat = self.get_chat(request, pk)
        form = ChatEditForm(instance=chat)
        return self._render(request, chat, form)

    def post(self, request, pk):
        chat = self.get_chat(request, pk)

        if chat.creator_id != request.user.id:
            return redirect('chat_info', pk=pk)

        form = ChatEditForm(request.POST, request.FILES, instance=chat)
        if form.is_valid():
            form.save()
            return redirect('chat_info', pk=pk)

        return self._render(request, chat, form)

    def _render(self, request, chat, form):
        members = chat.participants.select_related('profile').order_by('username')

        media_messages = chat.messages.filter(
            Q(image__gt='') | Q(video__gt=''),
        ).order_by('-created_at')

        return render(request, self.template_name, {
            'chat': chat,
            'members': members,
            'media_messages': media_messages,
            'is_creator': chat.creator_id == request.user.id,
            'form': form,
        })


class ChatAddParticipantView(LoginRequiredMixin, View):
    template_name = 'chat/add_participant.html'

    def get_chat(self, request, pk):
        return get_object_or_404(Chat, pk=pk, participants=request.user, is_group=True)

    def _addable_friends(self, request, chat):
        friend_ids = get_friend_ids(request.user)
        existing_ids = set(chat.participants.values_list('pk', flat=True))
        addable_ids = friend_ids - existing_ids
        return addable_ids, User.objects.filter(pk__in=addable_ids).select_related('profile')

    def get(self, request, pk):
        chat = self.get_chat(request, pk)
        _addable_ids, friends = self._addable_friends(request, chat)
        return render(request, self.template_name, {'chat': chat, 'friends': friends})

    def post(self, request, pk):
        chat = self.get_chat(request, pk)
        addable_ids, friends = self._addable_friends(request, chat)

        selected_ids = {uid for uid in request.POST.getlist('participants') if uid.isdigit()}
        selected_ids = {int(uid) for uid in selected_ids} & addable_ids

        if not selected_ids:
            return render(request, self.template_name, {
                'chat': chat,
                'friends': friends,
                'error': 'Оберіть хоча б одного друга.',
            })

        to_add = User.objects.filter(pk__in=selected_ids)
        chat.participants.add(*to_add)
        return redirect('chat_info', pk=pk)


class ChatDetailView(LoginRequiredMixin, View):
    template_name = 'chat/list.html'

    def get(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk, participants=request.user)

        chat.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)

        messages_qs = chat.messages.select_related('sender', 'sender__profile').order_by('created_at')

        other_user = None
        if not chat.is_group:
            other_user = chat.participants.exclude(pk=request.user.pk).first()

        primary_qs, requests_qs = _split_chats_for_sidebar(request.user)
        chat_data = _build_chat_sidebar_data(request.user, primary_qs)
        request_data = _build_chat_sidebar_data(request.user, requests_qs)

        is_incoming_pending, is_pending_awaiting, show_request_composer = _pending_flags(chat, request.user)

        return render(request, self.template_name, {
            'chat_data': chat_data,
            'request_data': request_data,
            'active_chat': chat,
            'messages_list': messages_qs,
            'other_user': other_user,
            'is_incoming_pending': is_incoming_pending,
            'is_pending_awaiting': is_pending_awaiting,
            'show_request_composer': show_request_composer,
        })


class ChatMessagesPollView(LoginRequiredMixin, View):
    template_name = 'chat/_messages.html'

    def get(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk, participants=request.user)
        chat.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
        messages_qs = chat.messages.select_related('sender', 'sender__profile').order_by('created_at')
        return render(request, self.template_name, {'messages_list': messages_qs, 'chat': chat})


class ChatPopupView(LoginRequiredMixin, View):
    template_name = 'chat/_popup_list.html'

    def get(self, request):
        primary_qs, _requests_qs = _split_chats_for_sidebar(request.user)
        chat_data = _build_chat_sidebar_data(request.user, primary_qs)
        return render(request, self.template_name, {'chat_data': chat_data})


class ChatPopupConversationView(LoginRequiredMixin, View):
    template_name = 'chat/_popup_conversation.html'

    def get(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk, participants=request.user)
        chat.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
        messages_qs = chat.messages.select_related('sender', 'sender__profile').order_by('created_at')

        other_user = None
        if not chat.is_group:
            other_user = chat.participants.exclude(pk=request.user.pk).first()

        is_incoming_pending, is_pending_awaiting, show_request_composer = _pending_flags(chat, request.user)

        return render(request, self.template_name, {
            'chat': chat,
            'messages_list': messages_qs,
            'other_user': other_user,
            'is_incoming_pending': is_incoming_pending,
            'is_pending_awaiting': is_pending_awaiting,
            'show_request_composer': show_request_composer,
        })


class ChatAcceptRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chat = get_object_or_404(
            Chat, pk=pk, participants=request.user,
            status=Chat.Status.PENDING,
        )
        if chat.creator_id != request.user.id:
            chat.status = Chat.Status.ACCEPTED
            chat.save(update_fields=['status'])

            Notification.objects.filter(
                recipient=request.user, sender_id=chat.creator_id,
                notification_type=Notification.NotificationType.MESSAGE, is_read=False,
            ).update(is_read=True)

        return redirect('chat_detail', pk=pk)

    def get(self, request, pk):
        return redirect('chat_detail', pk=pk)


class ChatDeclineRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chat = get_object_or_404(
            Chat, pk=pk, participants=request.user,
            status=Chat.Status.PENDING,
        )
        if chat.creator_id != request.user.id:
            Notification.objects.filter(
                recipient=request.user, sender_id=chat.creator_id,
                notification_type=Notification.NotificationType.MESSAGE, is_read=False,
            ).update(is_read=True)
            chat.delete()
        return redirect('chat_list')

    def get(self, request, pk):
        return redirect('chat_list')


class MessageSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk, participants=request.user)

        if not chat.is_group and chat.status == Chat.Status.PENDING:
            if chat.creator_id == request.user.id:
                if chat.messages.filter(sender=request.user).exists():
                    messages.error(
                        request,
                        'Ви вже надіслали запит на повідомлення. Зачекайте, поки його приймуть.',
                    )
                    return redirect('chat_detail', pk=pk)
            else:
                messages.error(
                    request,
                    'Спершу потрібно прийняти запит на повідомлення.',
                )
                return redirect('chat_detail', pk=pk)

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


class MessageDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, msg_id):
        message = get_object_or_404(Message, pk=msg_id, sender=request.user, chat_id=pk)
        message.delete()
        return redirect('chat_detail', pk=pk)

    def get(self, request, pk, msg_id):
        return redirect('chat_detail', pk=pk)


class ChatMarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk, participants=request.user)
        chat.messages.exclude(sender=request.user).update(is_read=True)
        return redirect('chat_detail', pk=pk)

    def get(self, request, pk):
        return redirect('chat_detail', pk=pk)


class ChatLeaveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk, participants=request.user)
        chat.participants.remove(request.user)
        if chat.participants.count() == 0:
            chat.delete()
        return redirect('chat_list')

    def get(self, request, pk):
        return redirect('chat_list')


class ChatDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chat = get_object_or_404(
            Chat, pk=pk, participants=request.user,
            is_group=True, creator=request.user,
        )
        chat.delete()
        return redirect('chat_list')

    def get(self, request, pk):
        return redirect('chat_list')


class PostShareView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        text = request.POST.get('text', '').strip()
        chat_ids = request.POST.getlist('chat_ids')

        chats = Chat.objects.filter(pk__in=chat_ids, participants=request.user)

        sent_to = 0
        for chat in chats:
            if not chat.is_group and chat.status == Chat.Status.PENDING:
                if chat.creator_id != request.user.id:
                    continue
                if chat.messages.filter(sender=request.user).exists():
                    continue

            Message.objects.create(chat=chat, sender=request.user, shared_post=post)
            if text:
                Message.objects.create(chat=chat, sender=request.user, text=text)
            sent_to += 1

        return JsonResponse({'ok': True, 'sent_to': sent_to})

    def get(self, request, pk):
        return redirect('post_detail', pk=pk)