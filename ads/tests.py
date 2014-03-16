#-*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.gis import geos
from django.contrib.gis.geos import GEOSGeometry

from .factories import AdFactory, SearchFactory, HabitationType
from .models import AdSearchRelation
from .utils import geo_from_address


class NotificationTestCase(TestCase):

    def test_ad_then_search(self):
        house, create = HabitationType.objects.get_or_create(label="Maison")
        apartment, create = HabitationType.objects.get_or_create(label="Appartement")
        # create an ad
        ad = AdFactory(address="22 rue esquirol Paris", price=600000, surface=60, habitation_type=apartment)
        # create a search with ad.location inside search.location
        search = SearchFactory(location=geos.MultiPolygon(ad.location.buffer(2)), price_max=700000, surface_min=50, habitation_types=[apartment, ])
        # here we should have results ...
        self.assertEqual(AdSearchRelation.objects.all().count(), 1)

    def test_search_then_ad(self):
        house, create = HabitationType.objects.get_or_create(label="Maison")
        apartment, create = HabitationType.objects.get_or_create(label="Appartement")
        # create a search with search.location contaning ad.location
        pnt = GEOSGeometry(geo_from_address("22 rue esquirol Paris"))
        search = SearchFactory(location=geos.MultiPolygon(pnt.buffer(2)), price_max=700000, surface_min=50, habitation_types=[apartment, ])
        # create an ad
        ad = AdFactory(address="22 rue esquirol Paris", price=600000, surface=60, habitation_type=apartment)
        # here we should have results ...
        self.assertEqual(AdSearchRelation.objects.all().count(), 1)

    def test_ad_then_search_then_update_ad(self):
        house, create = HabitationType.objects.get_or_create(label="Maison")
        apartment, create = HabitationType.objects.get_or_create(label="Appartement")
        # create an ad
        ad = AdFactory(address="22 rue esquirol Paris", price=600000, surface=60, habitation_type=apartment)
        pnt = GEOSGeometry(geo_from_address(u"52 W 52nd St, New York, NY 10019, États-Unis"))
        # create a search with ad.location inside search.location
        search = SearchFactory(location=geos.MultiPolygon(pnt.buffer(2)), price_max=700000, surface_min=50, habitation_types=[apartment, ])
        # here we should have results ...
        self.assertEqual(AdSearchRelation.objects.all().count(), 0)

        search.location = geos.MultiPolygon(ad.location.buffer(2))
        search.save()
        self.assertEqual(AdSearchRelation.objects.all().count(), 1)

    def test_search_then_ad_the_search_update(self):
        house, create = HabitationType.objects.get_or_create(label="Maison")
        apartment, create = HabitationType.objects.get_or_create(label="Appartement")
        # create a search with search.location contaning ad.location
        pnt = GEOSGeometry(geo_from_address("22 rue esquirol Paris"))
        search = SearchFactory(location=geos.MultiPolygon(pnt.buffer(2)), price_max=700000, surface_min=50, habitation_types=[apartment, ])
        # create an ad
        ad = AdFactory(address=u"52 W 52nd St, New York, NY 10019, États-Unis", price=600000, surface=60, habitation_type=apartment)
        # here we should have results ...
        self.assertEqual(AdSearchRelation.objects.all().count(), 0)
        ad.address = "22 rue esquirol Paris"
        ad.save()
        self.assertEqual(AdSearchRelation.objects.all().count(), 1)
