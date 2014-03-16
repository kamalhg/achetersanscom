#-*- coding: utf-8 -*-
import requests



from django import forms
from django.contrib.gis import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth import authenticate, login

from .utils import geo_from_address, WrongAddressError
from .models import Ad, Search, HabitationType, AdPicture
from .widgets import ExtendedLeafletWidget

#Utils


class AdPictureForm(forms.ModelForm):
    class Meta:
        model = AdPicture
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Description de la photo', }),
        }

class WithLogin(forms.ModelForm):
    # clean if username and password
    # or 3
    def clean(self):
        cleaned_data = super(WithLogin, self).clean()
        username = cleaned_data['username']
        email = cleaned_data['email']
        password = cleaned_data['password']
        password2 = cleaned_data['password2']
        login_username = cleaned_data['login_username']
        login_password = cleaned_data['login_password']

        login = cleaned_data['login']

        if login:
            # we are in login process
            a = authenticate(username=login_username, password=login_password)
            if not a:
                raise forms.ValidationError("Votre Nom d'utilisateur et/ou votre Mot de passe ne sont pas valides.")
                self.add_error('login_username', "skksskskk")
        else:
            # we are in signup process
            if password != password2:
                raise forms.ValidationError("Les mots de passe sont différents.")
            existing = User.objects.filter(username__iexact=username)
            if existing.exists():
                raise forms.ValidationError(_("A user with that username already exists."))

        return cleaned_data

    login = forms.BooleanField(required=False)  # keep state of user choice: signup or login

    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={}), required=False)
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={}), max_length=254, required=False)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput({}), required=False)
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput({}), required=False)

    login_username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={}), required=False)
    login_password = forms.CharField(label=_("Password"), widget=forms.PasswordInput({}), required=False)




class EditSearchForm(forms.ModelForm):
    habitation_types = forms.ModelMultipleChoiceField(queryset=HabitationType.objects.all(), widget=forms.CheckboxSelectMultiple(attrs={}))

    def clean_location(self):
        location = self.cleaned_data['location']
        if location.area > 300:
            raise forms.ValidationError("Entrer une zone de recherche plus petite")
        return location

    class Meta:
        model = Search
        exclude = ('user', )
        widgets = {
            'location': ExtendedLeafletWidget(),
            'price_max': forms.TextInput(attrs={'placeholder': 'Prix max.', }),
            'surface_min': forms.TextInput(attrs={'placeholder': 'Surface min.', }),
            'description': forms.Textarea({'placeholder': 'Description de votre recherche', })
        }


class EditSearchFormWithLogin(WithLogin, EditSearchForm):

    def clean(self):
        cleaned_data = super(EditSearchFormWithLogin, self).clean()
        print 'ok'
        return cleaned_data

    class Meta(EditSearchForm.Meta):
        widgets = EditSearchForm.Meta.widgets


class SearchSearchForm(forms.ModelForm):

    habitation_type = forms.ModelChoiceField(queryset=HabitationType.objects.all(), empty_label=None, widget=forms.RadioSelect(attrs={}))

    def clean_address(self):
        address = self.cleaned_data['address']
        try:
            geo_from_address(address)
        except WrongAddressError:
            raise forms.ValidationError("Entrer une adresse valide")
        return address

    class Meta:
        model = Ad
        fields = ('address', 'price', 'surface', 'habitation_type', )
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Adresse', }),
            'price': forms.TextInput(attrs={'placeholder': 'Prix', }),
            'surface': forms.TextInput(attrs={'placeholder': 'Surface', }),
        }


class EditAdForm(forms.ModelForm):

    habitation_type = forms.ModelChoiceField(label="Type de bien", queryset=HabitationType.objects.all(), empty_label=None, widget=forms.RadioSelect(attrs={}))

    def clean_address(self):
        address = self.cleaned_data['address']
        url = "http://services.gisgraphy.com//geocoding/geocode?address='%s'&country=FR&format=json" % address
        r = requests.get(url)
        try:
            json = r.json()
            lat = json['result'][0]['lat']
            lng = json['result'][0]['lng']
            pt = "POINT(%s %s)" % (lng, lat)
        except:
            raise forms.ValidationError("Entrer une adresse valide")
        return address

    class Meta:
        model = Ad
        exclude = ('user', 'location', )
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': u'Adresse complète',}),
            'price': forms.TextInput(attrs={'placeholder': 'Prix'}),
            'surface': forms.TextInput(attrs={'placeholder': 'Surface'}),
            'surface_carrez': forms.TextInput(attrs={'placeholder': 'Surface loi carrez'}),
            'rooms': forms.TextInput(attrs={'placeholder': u'Nb. de pièces'}),
            'bedrooms': forms.TextInput(attrs={'placeholder': u'Nb. de chambres'}),
            'energy_consumption': forms.Select(attrs={}),
            'ad_valorem_tax': forms.TextInput(attrs={'placeholder': u'Taxe foncière'}),
            'housing_tax': forms.TextInput(attrs={'placeholder': u'', }),
            'maintenance_charges': forms.TextInput(attrs={'placeholder': u'', }),
            'emission_of_greenhouse_gases': forms.Select(attrs={}),
            'ground_surface': forms.TextInput(attrs={'placeholder': u'', }),
            'floor': forms.TextInput(attrs={'placeholder': u'', }),
            'ground_floor': forms.CheckboxInput(),
            'top_floor': forms.CheckboxInput(),
            'not_overlooked': forms.CheckboxInput(),
            'elevator': forms.CheckboxInput(),
            'intercom': forms.CheckboxInput(),
            'digicode': forms.CheckboxInput(),
            'doorman': forms.CheckboxInput(),
            'heating': forms.Select(attrs={}),
            'kitchen': forms.CheckboxInput(),
            'duplex': forms.CheckboxInput(),
            'swimming_pool': forms.CheckboxInput(),
            'alarm': forms.CheckboxInput(),
            'air_conditioning': forms.CheckboxInput(),
            'fireplace': forms.Select(attrs={}),
            'terrace': forms.TextInput(attrs={'placeholder': u'', }),
            'balcony': forms.TextInput(attrs={'placeholder': u'', }),
            'separate_dining_room': forms.CheckboxInput(),
            'separate_toilet': forms.TextInput(attrs={'placeholder': u'', }),
            'bathroom': forms.TextInput(attrs={'placeholder': u'', }),
            'shower': forms.TextInput(attrs={'placeholder': u'', }),
            'separate_entrance': forms.CheckboxInput(),
            'cellar': forms.CheckboxInput(),
            'parking': forms.Select(attrs={}),
            'orientation': forms.TextInput(attrs={'placeholder': u'', }),
            'description': forms.Textarea({'placeholder': 'Compléments d\'information', })
        }


class EditAdFormWithLogin(WithLogin, EditAdForm):
    pass


class SearchAdForm(forms.ModelForm):

    def clean_location(self):
        location = self.cleaned_data['location']
        if location.area > 300:
            raise forms.ValidationError("Entrer une zone de recherche plus petite")
        return location

    habitation_types = forms.ModelMultipleChoiceField(queryset=HabitationType.objects.all(), widget=forms.CheckboxSelectMultiple(attrs={}))

    class Meta:
        model = Search
        fields = ('location', 'price_max', 'surface_min', 'habitation_types', )
        widgets = {
            'location': ExtendedLeafletWidget(),
            'price_max': forms.TextInput(attrs={'placeholder': 'Prix max.', }),
            'surface_min': forms.TextInput(attrs={'placeholder': 'Surface min.', }),
        }


class ContactForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)

