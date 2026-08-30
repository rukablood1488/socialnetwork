from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import *


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)



# СПОВІЩЕННЯ
 
@receiver(post_save, sender=Like)
def notify_on_like(sender, instance, created, **kwargs):
    if not created:
        return
    post = instance.post
    if instance.user_id == post.author_id:
        return
    Notification.objects.create(
        recipient=post.author,
        sender=instance.user,
        notification_type=Notification.NotificationType.LIKE,
        post=post,
        text=f'{instance.user.username} вподобав(ла) вашу публікацію',
    )
 
 
@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    if not created:
        return
    post = instance.post
    if instance.author_id == post.author_id:
        return
    Notification.objects.create(
        recipient=post.author,
        sender=instance.author,
        notification_type=Notification.NotificationType.COMMENT,
        post=post,
        text=f'{instance.author.username} прокоментував(ла) вашу публікацію',
    )
 
 
@receiver(post_save, sender=Repost)
def notify_on_repost(sender, instance, created, **kwargs):
    if not created:
        return
    post = instance.post
    if instance.user_id == post.author_id:
        return
    Notification.objects.create(
        recipient=post.author,
        sender=instance.user,
        notification_type=Notification.NotificationType.REPOST,
        post=post,
        text=f'{instance.user.username} поширив(ла) вашу публікацію',
    )
 
 
@receiver(post_save, sender=Subscription)
def notify_on_subscribe(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.status == Subscription.Status.PENDING:
        text = f'{instance.follower.username} надіслав(ла) запит на стеження'
    else:
        text = f'{instance.follower.username} підписався(лась) на вас'
 
    Notification.objects.create(
        recipient=instance.following,
        sender=instance.follower,
        notification_type=Notification.NotificationType.SUBSCRIBE,
        text=text,
    )


def _messages_word(n):
    n_abs = abs(n) % 100
    n1 = n_abs % 10
    if 11 <= n_abs <= 14 or n1 == 0 or n1 >= 5:
        return 'повідомлень'
    return 'повідомлення'


@receiver(post_save, sender=Message)
def notify_on_message(sender, instance, created, **kwargs):
    if not created:
        return

    chat = instance.chat

    is_request = (
        not chat.is_group
        and chat.status == Chat.Status.PENDING
        and chat.creator_id == instance.sender_id
    )

    recipients = chat.participants.exclude(pk=instance.sender_id)

    for recipient in recipients:
        if is_request:
            Notification.objects.create(
                recipient=recipient,
                sender=instance.sender,
                notification_type=Notification.NotificationType.MESSAGE,
                text=f'{instance.sender.username} надіслав(ла) запит на повідомлення',
            )
            continue


        unread_count = Message.objects.filter(
            chat=chat, sender=instance.sender, is_read=False,
        ).count()

        text = f'Переглянь {unread_count} {_messages_word(unread_count)} від {instance.sender.username}'

        existing = Notification.objects.filter(
            recipient=recipient,
            sender=instance.sender,
            notification_type=Notification.NotificationType.MESSAGE,
            is_read=False,
        ).order_by('-created_at').first()

        if existing:
            existing.text = text
            existing.created_at = timezone.now()
            existing.save(update_fields=['text', 'created_at'])
        else:
            Notification.objects.create(
                recipient=recipient,
                sender=instance.sender,
                notification_type=Notification.NotificationType.MESSAGE,
                text=text,
            )