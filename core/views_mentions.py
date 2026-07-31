from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View


class MentionSuggestView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        results = []

        if query:
            users = User.objects.filter(
                username__istartswith=query,
            ).exclude(pk=request.user.pk).select_related('profile')[:6]

            for u in users:
                profile = getattr(u, 'profile', None)
                avatar_url = ''
                if profile and profile.avatar:
                    avatar_url = profile.avatar.url

                results.append({
                    'username': u.username,
                    'avatar_url': avatar_url,
                    'full_name': u.get_full_name(),
                })

        return JsonResponse({'results': results})