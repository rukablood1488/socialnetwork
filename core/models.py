from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



# ПРОФІЛЬ КОРИСТУВАЧА


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



# ПОСТИ


class Post(models.Model):

    class ContentType(models.TextChoices):
        TEXT  = 'text',  'Текст'
        IMAGE = 'image', 'Зображення'
        VIDEO = 'video', 'Відео'
        LINK  = 'link',  'Посилання'

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
   
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Група',
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



# ЛАЙКИ


class Like(models.Model):
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Користувач',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Публікація',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата лайку',
    )

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user.username} → пост #{self.post_id}'



# КОМЕНТАРІ


class Comment(models.Model):
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публікація',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        blank=True,
        null=True,
        verbose_name='Батьківський коментар',
    )
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата коментаря',
    )

    class Meta:
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'
        ordering = ['created_at']

    def __str__(self):
        return f'Коментар #{self.pk} від {self.author.username}'



# РЕПОСТИ


class Repost(models.Model):
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reposts',
        verbose_name='Користувач',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='reposts',
        verbose_name='Оригінальна публікація',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата репосту',
    )

    class Meta:
        verbose_name = 'Репост'
        verbose_name_plural = 'Репости'
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user.username} поширив пост #{self.post_id}'



# ДРУЗІ ТА ПІДПИСКИ


class Friendship(models.Model):

    class Status(models.TextChoices):
        PENDING  = 'pending',  'Очікує підтвердження'
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



# ГРУПИ ТА СПІЛЬНОТИ


class Group(models.Model):
    
    name = models.CharField(
        max_length=150,
        verbose_name='Назва групи',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Опис',
    )
    cover = models.ImageField(
        upload_to='groups/covers/',
        blank=True,
        null=True,
        verbose_name='Обкладинка групи',
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_groups',
        verbose_name='Засновник',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення',
    )

    class Meta:
        verbose_name = 'Група'
        verbose_name_plural = 'Групи'
        ordering = ['name']

    def __str__(self):
        return self.name


class GroupMembership(models.Model):

    class Role(models.TextChoices):
        MEMBER = 'member', 'Учасник'
        ADMIN  = 'admin',  'Адміністратор'

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='Група',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='group_memberships',
        verbose_name='Користувач',
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER,
        verbose_name='Роль',
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата вступу',
    )

    class Meta:
        verbose_name = 'Членство в групі'
        verbose_name_plural = 'Членства в групах'
        unique_together = ('group', 'user')

    def __str__(self):
        return f'{self.user.username} у групі "{self.group.name}" [{self.get_role_display()}]'



# ЧАТ ТА ПОВІДОМЛЕННЯ


class Chat(models.Model):
    
    name = models.CharField(
        max_length=150,
        blank=True,
        default='',
        verbose_name='Назва чату (для групових)',
    )
    is_group = models.BooleanField(
        default=False,
        verbose_name='Груповий чат',
    )
    participants = models.ManyToManyField(
        User,
        related_name='chats',
        verbose_name='Учасники',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення',
    )

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чати'
        ordering = ['-created_at']

    def __str__(self):
        if self.is_group:
            return f'Груповий чат: {self.name or f"#{self.pk}"}'
        return f'Приватний чат #{self.pk}'


class Message(models.Model):
    
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Чат',
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Відправник',
    )
    text = models.TextField(
        blank=True,
        default='',
        verbose_name='Текст',
    )
    image = models.ImageField(
        upload_to='messages/images/',
        blank=True,
        null=True,
        verbose_name='Зображення',
    )
    video = models.FileField(
        upload_to='messages/videos/',
        blank=True,
        null=True,
        verbose_name='Відео',
    )
    file = models.FileField(
        upload_to='messages/files/',
        blank=True,
        null=True,
        verbose_name='Файл',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата відправлення',
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Прочитано',
    )

    class Meta:
        verbose_name = 'Повідомлення'
        verbose_name_plural = 'Повідомлення'
        ordering = ['created_at']

    def __str__(self):
        return f'Повідомлення #{self.pk} від {self.sender.username} у чаті #{self.chat_id}'



# СПОВІЩЕННЯ


class Notification(models.Model):

    class NotificationType(models.TextChoices):
        FRIEND_REQUEST = 'friend_request', 'Запит у друзі'
        FRIEND_ACCEPT  = 'friend_accept',  'Запит прийнято'
        LIKE           = 'like',           'Лайк'
        COMMENT        = 'comment',        'Коментар'
        REPOST         = 'repost',         'Репост'
        MESSAGE        = 'message',        'Нове повідомлення'
        GROUP_INVITE   = 'group_invite',   'Запрошення до групи'

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Отримувач',
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True,
        verbose_name='Ініціатор події',
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        verbose_name='Тип сповіщення',
    )
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Пов\'язана публікація',
    )
    text = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Текст сповіщення',
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Прочитано',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата',
    )

    class Meta:
        verbose_name = 'Сповіщення'
        verbose_name_plural = 'Сповіщення'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_notification_type_display()}] для {self.recipient.username}'



# ВІДГУКИ ТА РЕЙТИНГ


class Review(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор відгуку',
    )
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='reviews',
        blank=True,
        null=True,
        verbose_name='Публікація',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='reviews',
        blank=True,
        null=True,
        verbose_name='Група',
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name='Оцінка (1–5)',
    )
    text = models.TextField(
        blank=True,
        default='',
        verbose_name='Текст відгуку',
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name='Схвалено адміністратором',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата відгуку',
    )

    class Meta:
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'
        ordering = ['-created_at']

    def __str__(self):
        target = f'пост #{self.post_id}' if self.post_id else f'групу "{self.group}"'
        return f'Відгук від {self.author.username} на {target} ({self.rating}★)'