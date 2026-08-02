from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .models import Notification


class NotificationsView(LoginRequiredMixin, View):
    template_name = 'notifications/list.html'

    def get(self, request):
        notifications = Notification.objects.filter(
            recipient=request.user,
        ).select_related('sender', 'sender__profile', 'post').order_by('-created_at')

        return render(request, self.template_name, {'notifications': notifications})


class NotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()

        if notification.post_id:
            return redirect('post_detail', pk=notification.post_id)
        if notification.sender_id:
            return redirect('profile', username=notification.sender.username)
        return redirect('notifications')

    def get(self, request, pk):
        return redirect('notifications')


class NotificationsReadAllView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(
            recipient=request.user, is_read=False,
        ).update(is_read=True)
        return redirect('notifications')

    def get(self, request):
        return redirect('notifications')