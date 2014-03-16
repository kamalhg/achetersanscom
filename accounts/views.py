from .models import UserProfile
from django.views.generic import DetailView, UpdateView
from django.shortcuts import redirect
from ads.models import Ad, Search
from ads.views import AssureOwnerMixin
from .forms import EditUserAccountForm

class UserAccount(DetailView):
    slug_field = 'user__username'
    model = UserProfile

    def get_context_data(self, **kwargs):
        context = super(UserAccount, self).get_context_data(**kwargs)
        user_profile = self.get_object()
        context['ads'] = Ad.objects.filter(user=user_profile.user)
        context['searches'] = Search.objects.filter(user=user_profile.user)
        return context


class UpdateUserAccount(AssureOwnerMixin, UpdateView):
    slug_field = 'user__username'
    form_class = EditUserAccountForm
    model = UserProfile


def redirect_profile(request):
    user = request.user
    return redirect('user_account', slug=user.username)
