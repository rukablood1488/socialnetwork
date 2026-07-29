from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render
from django.views import View

from .models import Group


class SearchView(LoginRequiredMixin, View):
    template_name = 'search/index.html'

    def get(self, request):
        return render(request, self.template_name, {})


class SearchResultsView(LoginRequiredMixin, View):
    template_name = 'search/_results.html'

    def get(self, request):
        query = request.GET.get('q', '').strip()

        users = []
        groups = []

        if query:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).exclude(pk=request.user.pk).select_related('profile')[:15]

            groups = Group.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )[:15]

        return render(request, self.template_name, {
            'query': query,
            'users': users,
            'groups': groups,
        })