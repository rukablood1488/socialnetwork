from django.contrib import admin
from .models import (
    UserProfile,
    Post,
    Like,
    Comment,
    Repost,
    Friendship,
    Subscription,
    Group,
    GroupMembership,
    Chat,
    Message,
    Notification,
    Review,
)



# ПРОФІЛЬ


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'birth_date')
    search_fields = ('user__username', 'user__email', 'bio')
    raw_id_fields = ('user',)



# ПОСТИ, ЛАЙКИ, КОМЕНТАРІ, РЕПОСТИ


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display   = ('id', 'author', 'content_type', 'group', 'created_at')
    list_filter    = ('content_type', 'created_at')
    search_fields  = ('author__username', 'text')
    raw_id_fields  = ('author', 'group')
    date_hierarchy = 'created_at'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display  = ('user', 'post', 'created_at')
    raw_id_fields = ('user', 'post')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ('id', 'author', 'post', 'parent', 'created_at')
    search_fields = ('author__username', 'text')
    raw_id_fields = ('author', 'post', 'parent')


@admin.register(Repost)
class RepostAdmin(admin.ModelAdmin):
    list_display  = ('user', 'post', 'created_at')
    raw_id_fields = ('user', 'post')



# ДРУЗІ ТА ПІДПИСКИ


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display  = ('sender', 'receiver', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('sender__username', 'receiver__username')
    raw_id_fields = ('sender', 'receiver')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display  = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    raw_id_fields = ('follower', 'following')



# ГРУПИ


class GroupMembershipInline(admin.TabularInline):
    model      = GroupMembership
    extra      = 0
    raw_id_fields = ('user',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display  = ('name', 'creator', 'created_at')
    search_fields = ('name', 'description', 'creator__username')
    raw_id_fields = ('creator',)
    inlines       = [GroupMembershipInline]


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display  = ('user', 'group', 'role', 'joined_at')
    list_filter   = ('role',)
    search_fields = ('user__username', 'group__name')
    raw_id_fields = ('user', 'group')



# ЧАТ ТА ПОВІДОМЛЕННЯ


class MessageInline(admin.TabularInline):
    model         = Message
    extra         = 0
    readonly_fields = ('sender', 'created_at')
    fields        = ('sender', 'text', 'is_read', 'created_at')


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'is_group', 'created_at')
    list_filter   = ('is_group',)
    search_fields = ('name',)
    filter_horizontal = ('participants',)
    inlines       = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ('id', 'sender', 'chat', 'is_read', 'created_at')
    list_filter   = ('is_read',)
    search_fields = ('sender__username', 'text')
    raw_id_fields = ('sender', 'chat')



# СПОВІЩЕННЯ


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('recipient', 'sender', 'notification_type', 'is_read', 'created_at')
    list_filter   = ('notification_type', 'is_read')
    search_fields = ('recipient__username', 'sender__username', 'text')
    raw_id_fields = ('recipient', 'sender', 'post')



# ВІДГУКИ


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display   = ('author', 'post', 'group', 'rating', 'is_approved', 'created_at')
    list_filter    = ('rating', 'is_approved')
    search_fields  = ('author__username', 'text')
    raw_id_fields  = ('author', 'post', 'group')
    list_editable  = ('is_approved',)
    actions        = ['approve_reviews', 'reject_reviews']

    @admin.action(description='Схвалити вибрані відгуки')
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Відхилити вибрані відгуки')
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)