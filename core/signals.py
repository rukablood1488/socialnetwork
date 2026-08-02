from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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