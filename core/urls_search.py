from django.urls import path
from . import views_search


search_urls = [
    path('search/', views_search.SearchView.as_view(), name='search'),

    path('search/results/', views_search.SearchResultsView.as_view(), name='search_results'),
]