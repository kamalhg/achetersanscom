#-*- coding: utf-8 -*-

import datetime
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet

from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import (CreateView, DetailView, UpdateView,
                                  DeleteView, FormView, ListView)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from accounts.models import UserProfile

from .models import Ad, AdPicture, Search, AdSearchRelation
from .forms import EditAdForm, EditAdFormWithLogin, EditSearchForm, EditSearchFormWithLogin, ContactForm, SearchSearchForm, SearchAdForm, AdPictureForm


# Mixins
class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        print 'LoginRequiredMixin'
        return super(LoginRequiredMixin, self).dispatch(request, *args,
                                                        **kwargs)


class SetUserMixin(object):
    """
    Both form_valid and forms_valid are required, to deal with
    CreateWithInlinesView and UpdateWithInlinesView implementation.
    """

    def get_or_create_and_login_user(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        email = form.cleaned_data['email']
        login_username = form.cleaned_data['login_username']
        login_password = form.cleaned_data['login_password']
        _login = form.cleaned_data['login']

        if _login:
            user = authenticate(username=login_username, password=login_password)
        else:
            user = User.objects.create_user(username, email, password)
            user = authenticate(username=username, password=password)
            UserProfile(user=user).save()
        login(self.request, user)

    def forms_valid(self, form, inlines):
        if self.request.user.is_anonymous():
            self.get_or_create_and_login_user(form)
        form.instance.user = self.request.user
        return super(SetUserMixin, self).form_valid(form)

    def form_valid(self, form):
        if self.request.user.is_anonymous():
            self.get_or_create_and_login_user(form)
        form.instance.user = self.request.user
        return super(SetUserMixin, self).form_valid(form)


class AssureOwnerMixin(object):
    def get_object(self, queryset=None):
        print 'AssureOwnerMixin'
        """ Hook to ensure object is owned by request.user. """
        obj = self.model.objects.get(**{self.slug_field: self.kwargs['slug']})
        if not obj.user == self.request.user:
            raise Http404
        return obj


class FillInitialForm(object):
    def get_initial(self):
        initial = super(FillInitialForm, self).get_context_data()
        if self.request.GET:
            form = self.form_class(self.request.GET)
            return form.data.dict()
        return initial

# Utils
class MessageView(SingleObjectMixin, FormView):

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()
        self.object = self.get_object()
        self.request = request
        return super(MessageView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            # TODO: need to test if we can send this mail !
            # is user it autorized to = if ad/search fit together
            message = form.cleaned_data['message']
            sender = self.request.user.email
            recipients = [self.get_object().user.email, ]
            subject = "[AcheterSansCom] Message à propos de %s" % self.get_object()
            mail = EmailMessage(subject, message, sender, recipients, [sender])
            mail.send()
            # here we must set 'contacted'
            # UGLY ...
            if self.model == Search:
                asr = AdSearchRelation.objects.filter(search=self.object, ad__user=self.request.user)
                asr.update(search_contacted=datetime.datetime.now())
            else:
                asr = AdSearchRelation.objects.filter(ad=self.object, search__user=self.request.user)
                asr.update(ad_contacted=datetime.datetime.now())


        return super(MessageView, self).form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class MessageDetailView(DetailView):
    model = Ad
    contact_form = ContactForm
    detail_view = None

    def get(self, request, *args, **kwargs):
        view = self.detail_view.as_view(model=self.model, contact_form=self.contact_form, template_name=self.template_name)
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = MessageView.as_view(model=self.model, form_class=self.contact_form)
        return view(request, *args, **kwargs)


class AdPictureInline(InlineFormSet):
    """ Ad Picture InlineFormSet """
    model = AdPicture
    form = AdPictureForm
    extra = 4
    max_num = 4


# Ad
class CreateAdView(SetUserMixin, FillInitialForm, CreateWithInlinesView):
    model = Ad
    form_class = EditAdForm
    inlines = [AdPictureInline, ]

    def get_form_class(self):
        if self.request.user.is_anonymous():
            self.form_class = EditAdFormWithLogin
        else:
            self.form_class = EditAdForm
        return self.form_class


class ReadAdView(DetailView):
    model = Ad
    contact_form = ContactForm

    def get_context_data(self, **kwargs):
        context = super(ReadAdView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            ars = AdSearchRelation.objects.filter(ad=self.object, search__user=self.request.user, valid=True)
            if ars.count() > 0:
                if any(ars.values_list('ad_contacted', flat=True)):
                    context['already_contacted'] = True
                context['contact_form'] = self.contact_form()
        return context


class AdDetailView(MessageDetailView):
    model = Ad
    detail_view = ReadAdView


class UpdateAdView(LoginRequiredMixin, AssureOwnerMixin, UpdateWithInlinesView):
    model = Ad
    form_class = EditAdForm
    inlines = [AdPictureInline, ]


class DeleteAdView(LoginRequiredMixin, AssureOwnerMixin, DeleteView):
    model = Ad

    def get_success_url(self):
        slug = self.request.user.username
        return reverse_lazy('user_account', kwargs={'slug':slug, })


class AdListView(ListView):
    model = Ad
    paginate_by = 10

    _valid = False
    _urlencode_get = ''

    def get(self, request, *args, **kwargs):
        get = super(AdListView, self).get(request, *args, **kwargs)
        if 'save_ad' in self.request.GET and self._valid:
            q = self.request.GET.urlencode()
            return HttpResponseRedirect(reverse('ads_search_add') + '?%s' % q)
        return get

    def get_queryset(self):
        q = super(AdListView, self).get_queryset().order_by('-modified')
        # here we remove the page from request.GET
        data = self.request.GET.copy()
        if 'page' in data:
            del data['page']
        self.form = SearchAdForm(data or None)
        if self.form.is_valid():
            price_max = self.form.cleaned_data['price_max']
            surface_min = self.form.cleaned_data['surface_min']
            habitation_types = self.form.cleaned_data['habitation_types']
            location = self.form.cleaned_data['location']
            self._urlencode_get = data.urlencode()
            q = q.filter(price__lte=price_max).filter(surface__gte=surface_min).filter(habitation_type__in=habitation_types)
            self._valid = True
        return q

    def get_context_data(self, **kwargs):
        context = super(AdListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        context['valid'] = self._valid
        if self._urlencode_get != '':
            context['urlencode_get'] = '&%s' % self._urlencode_get
        return context

# Search
class CreateSearchView(SetUserMixin, FillInitialForm, CreateView):
    model = Search

    def get_form_class(self):
        if self.request.user.is_anonymous():
            self.form_class = EditSearchFormWithLogin
        else:
            self.form_class = EditSearchForm
        return self.form_class


class ReadSearchView(DetailView):
    model = Search
    contact_form = ContactForm

    def get_context_data(self, **kwargs):
        # here we test if logged user can contact search owner
        context = super(ReadSearchView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            ars = AdSearchRelation.objects.filter(search=self.object, ad__user=self.request.user, valid=True)
            if ars.count() > 0:
                # if multiple offers from same vendor feet same search
                # the vendor can only contact searcher one time
                # this is what the line below does
                if any(ars.values_list('search_contacted', flat=True)):
                    context['already_contacted'] = True
                context['contact_form'] = self.contact_form()
        return context


class SearchListView(ListView):
    model = Search
    paginate_by = 10

    _valid = False
    _urlencode_get = ''

    def get(self, request, *args, **kwargs):
        get = super(SearchListView, self).get(request, *args, **kwargs)
        if 'save_ad' in self.request.GET and self._valid:
            q = self.request.GET.urlencode()
            return HttpResponseRedirect(reverse('ads_ad_add') + '?%s' % q)
        return get

    def get_queryset(self):
        q = super(SearchListView, self).get_queryset().order_by('-modified')
        data = self.request.GET.copy()
        if 'page' in data:
            del data['page']
        self.form = SearchSearchForm(data or None)
        if self.form.is_valid():
            price = self.form.cleaned_data['price']
            surface = self.form.cleaned_data['surface']
            habitation_type = self.form.cleaned_data['habitation_type']
            address = self.form.cleaned_data['address']
            self._urlencode_get = data.urlencode()
            q = q.filter(price_max__gte=price).filter(surface_min__lte=surface).filter(habitation_types=habitation_type)
            self._valid = True
        return q

    def get_context_data(self, **kwargs):
        context = super(SearchListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        context['valid'] = self._valid
        if self._urlencode_get != '':
            context['urlencode_get'] = '&%s' % self._urlencode_get
        return context


class SearchDetailView(MessageDetailView):
    model = Search
    detail_view = ReadSearchView


class UpdateSearchView(LoginRequiredMixin, AssureOwnerMixin, UpdateView):
    model = Search
    form_class = EditSearchForm


class DeleteSearchView(LoginRequiredMixin, AssureOwnerMixin, DeleteView):
    model = Search

    def get_success_url(self):
        slug = self.request.user.username
        return reverse_lazy('user_account', kwargs={'slug':slug, })
