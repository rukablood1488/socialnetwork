from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Користувач',
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар',
    )
    cover = models.ImageField(
        upload_to='covers/',
        blank=True,
        null=True,
        verbose_name='Обкладинка',
    )
    bio = models.TextField(
        blank=True,
        default='',
        verbose_name='Біографія',
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата народження',
    )

    class Meta:
        verbose_name = 'Профіль користувача'
        verbose_name_plural = 'Профілі користувачів'

    def __str__(self):
        return f'Профіль: {self.user.username}'


class Post(models.Model):

    class ContentType(models.TextChoices):
        TEXT = 'text', 'Текст'
        IMAGE = 'image', 'Зображення'
        VIDEO = 'video', 'Відео'
        LINK = 'link', 'Посилання'

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    text = models.TextField(
        blank=True,
        default='',
        verbose_name='Текст публікації',
    )
    image = models.ImageField(
        upload_to='posts/images/',
        blank=True,
        null=True,
        verbose_name='Зображення',
    )
    video = models.FileField(
        upload_to='posts/videos/',
        blank=True,
        null=True,
        verbose_name='Відео',
    )
    link = models.URLField(
        blank=True,
        default='',
        verbose_name='Посилання',
    )
    content_type = models.CharField(
        max_length=10,
        choices=ContentType.choices,
        default=ContentType.TEXT,
        verbose_name='Тип контенту',
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата публікації',
    )

    class Meta:
        verbose_name = 'Публікація'
        verbose_name_plural = 'Публікації'
        ordering = ['-created_at']

    def __str__(self):
        return f'Пост #{self.pk} від {self.author.username} ({self.get_content_type_display()})'


class Friendship(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Очікує підтвердження'
        ACCEPTED = 'accepted', 'Прийнято'

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests',
        verbose_name='Відправник',
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_friend_requests',
        verbose_name='Отримувач',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата запиту',
    )

    class Meta:
        verbose_name = 'Дружба'
        verbose_name_plural = 'Дружба'
        unique_together = ('sender', 'receiver')
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'{self.sender.username} → {self.receiver.username} '
            f'[{self.get_status_display()}]'
        )


class Subscription(models.Model):

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Підписник',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='На кого підписаний',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата підписки',
    )

    class Meta:
        verbose_name = 'Підписка'
        verbose_name_plural = 'Підписки'
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.follower.username} стежить за {self.following.username}'