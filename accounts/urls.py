from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from registration.backends.simple.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail
from django.views.generic.base import TemplateView
from .views import UserAccount, UpdateUserAccount
from .models import UserProfile


class CustomRegistrationView(RegistrationView):
    form_class = RegistrationFormUniqueEmail
    def get_success_url(self, request, user):
        # create the profile
        UserProfile(user=user).save()
        return reverse_lazy('home')

# account url
urlpatterns = patterns('',
    url(r'^profile/$', 'accounts.views.redirect_profile'),
    # login/logout
    url(r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page':reverse_lazy('home')},
        name='logout'),
    url(r'^login/$',
        'django.contrib.auth.views.login',
        {'template_name': 'accounts/auth/login.html'},
        name='login'),

    # change password
    url(r'^password_change_done/$',
        'django.contrib.auth.views.password_change_done',
        {'template_name':'accounts/auth/password_change_done.html'},
        name="password_change_done"),
    url(r'^password_change/$',
        'django.contrib.auth.views.password_change',
        {'template_name':'accounts/auth/password_change.html',
         'post_change_redirect':reverse_lazy('password_change_done')},
        name="password_change"),

    # reset password
    url(r'^password_reset/$',
        'django.contrib.auth.views.password_reset',
        {'template_name':'accounts/auth/password_reset_form.html',
         'post_reset_redirect':reverse_lazy('password_reset_done')},
        name="password_reset"),
    url(r'^password_reset_done/$',
        'django.contrib.auth.views.password_reset_done',
        {'template_name':'accounts/auth/password_reset_done.html'},
        name="password_reset_done"),
    url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name':'accounts/auth/password_reset_confirm.html',
         'post_reset_redirect':reverse_lazy('password_reset_complete')},
        name="password_reset_confirm"),
    url(r'^password_reset_complete/$',
        'django.contrib.auth.views.password_reset_complete',
        {'template_name':'accounts/auth/password_reset_complete.html'},
        name="password_reset_complete"),

    # registration
    url(r'^register/$', CustomRegistrationView.as_view(), name='registration_register'),
    url(r'^register/closed/$',
                           TemplateView.as_view(template_name='registration/registration_closed.html'),
                           name='registration_disallowed'),
    (r'', include('registration.auth_urls')),
    # user account
    url(r'^(?P<slug>[\w-]+)/edit/$', UpdateUserAccount.as_view(), name="user_account_update"),
    url(r'^(?P<slug>[\w-]+)/$', UserAccount.as_view(), name="user_account"),

)
