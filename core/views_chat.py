from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .models import Chat, Message


class ChatListView(LoginRequiredMixin, View):
    template_name = 'chat/list.html'

    def get(self, request):
        chats = Chat.objects.filter(
            participants=request.user,
        ).prefetch_related(
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
                other_user = chat.participants.exclude(pk=request.user.pk).first()

            last_message = chat.messages.last()
            unread_count = chat.messages.exclude(sender=request.user).filter(is_read=False).count()

            chat_data.append({
                'chat': chat,
                'other_user': other_user,
                'last_message': last_message,
                'unread_count': unread_count,
            })

        return render(request, self.template_name, {'chat_data': chat_data})


class ChatNewView(LoginRequiredMixin, View):
    template_name = 'chat/new.html'

    def get(self, request):
        return render(request, self.template_name, {})


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

        chat = Chat.objects.create(is_group=False)
        chat.participants.add(request.user, target)
        return redirect('chat_detail', pk=chat.pk)

    def get(self, request, user_id):
        return self.post(request, user_id)


class ChatCreateGroupView(LoginRequiredMixin, View):
    template_name = 'chat/create_group.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        name = request.POST.get('name', '').strip()
        user_ids = [uid for uid in request.POST.getlist('participants') if uid.isdigit()]
        participants = User.objects.filter(pk__in=user_ids).exclude(pk=request.user.pk)

        if not participants.exists():
            return render(request, self.template_name, {
                'error': 'Оберіть хоча б одного учасника.',
            })

        chat = Chat.objects.create(name=name, is_group=True)
        chat.participants.add(request.user, *participants)
        return redirect('chat_detail', pk=chat.pk)


class ChatDetailView(LoginRequiredMixin, View):
    template_name = 'chat/detail.html'

    def get(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk, participants=request.user)

        chat.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)

        messages_qs = chat.messages.select_related('sender', 'sender__profile').order_by('created_at')

        other_user = None
        if not chat.is_group:
            other_user = chat.participants.exclude(pk=request.user.pk).first()

        return render(request, self.template_name, {
            'chat': chat,
            'messages_list': messages_qs,
            'other_user': other_user,
        })


class ChatMessagesPollView(LoginRequiredMixin, View):
    template_name = 'chat/_messages.html'

    def get(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk, participants=request.user)
        chat.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
        messages_qs = chat.messages.select_related('sender', 'sender__profile').order_by('created_at')
        return render(request, self.template_name, {'messages_list': messages_qs, 'chat': chat})


class MessageSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk, participants=request.user)

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