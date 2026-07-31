import re

from django import template
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

MENTION_RE = re.compile(r'@(\w+)')


@register.filter(name='linkify_mentions')
def linkify_mentions(text):
    if not text:
        return text

    usernames = set(MENTION_RE.findall(text))
    if not usernames:
        return escape(text)

    existing = set(
        User.objects.filter(username__in=usernames).values_list('username', flat=True)
    )

    safe_text = escape(text)

    def replace(match):
        username = match.group(1)
        if username in existing:
            url = reverse('profile', kwargs={'username': username})
            return f'<a href="{url}" class="fw-semibold text-decoration-none">@{username}</a>'
        return match.group(0)

    linked = MENTION_RE.sub(replace, safe_text)
    return mark_safe(linked)