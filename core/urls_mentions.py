from django.urls import path
from . import views_mentions


mention_urls = [
    path('mentions/suggest/', views_mentions.MentionSuggestView.as_view(), name='mention_suggest'),
]