from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from .views import *


urlpatterns = patterns('',

    # Ad
    url(r'^ad/add/$', CreateAdView.as_view(), name="ads_ad_add"),
    url(r'^ad/detail/(?P<slug>[-_\w]+)/$', AdDetailView.as_view(), name="ads_ad_detail"),
    url(r'^ad/edit/(?P<slug>[-_\w]+)/$', UpdateAdView.as_view(), name="ads_ad_update"),
    url(r'^ad/delete/(?P<slug>[-_\w]+)/$', DeleteAdView.as_view(), name="ads_ad_delete"),
    url(r'^ad/list/$', AdListView.as_view(), name="ads_ad_list"),
    # Search
    url(r'^search/add/$', CreateSearchView.as_view(), name="ads_search_add"),
    url(r'^search/detail/(?P<slug>[-_\w]+)/$', SearchDetailView.as_view(), name="ads_search_detail"),
    url(r'^search/edit/(?P<slug>[-_\w]+)/$', UpdateSearchView.as_view(), name="ads_search_update"),
    url(r'^search/delete/(?P<slug>[-_\w]+)/$', DeleteSearchView.as_view(), name="ads_search_delete"),
    url(r'^search/list/$', SearchListView.as_view(), name="ads_search_list")
)
