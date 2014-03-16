import string

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

import factory
from factory.fuzzy import *
from ads.models import ENERGY_CONSUMPTION_CHOICES, EMISSION_OF_GREENHOUSE_GASES_CHOICES, HEATING_CHOICES, KITCHEN_CHOICES, PARKING_CHOICES, FIREPLACE_CHOICES, HabitationType

from accounts.models import UserProfile

from .utils import address_from_geo


FUZZY_ENERGY_CONSUMPTION_CHOICES = dict(ENERGY_CONSUMPTION_CHOICES).keys()
FUZZY_EMISSION_OF_GREENHOUSE_GASES_CHOICES = dict(EMISSION_OF_GREENHOUSE_GASES_CHOICES).keys()
FUZZY_HEATING_CHOICES = dict(HEATING_CHOICES).keys()
FUZZY_KITCHEN_CHOICES = dict(KITCHEN_CHOICES).keys()
FUZZY_PARKING_CHOICES = dict(PARKING_CHOICES).keys()
FUZZY_FIREPLACE_CHOICES = dict(FIREPLACE_CHOICES).keys()


house, created = HabitationType.objects.get_or_create(label="Maison")
apartment, created = HabitationType.objects.get_or_create(label="Appartement")

TOP = 51.089166
LEFT = 9.560067799999999
BOTTOM = 41.3423276
RIGHT = -5.141227900000001

class FuzzyPoint(FuzzyText):
    def fuzz(self):
        return 'POINT (' + '%s %s' % (random.uniform(LEFT, RIGHT)  , random.uniform(TOP, BOTTOM)  ) + ')'


class FuzzyAddress(FuzzyText):
    def fuzz(self):
        lng = random.uniform(LEFT, RIGHT)
        lat = random.uniform(TOP, BOTTOM)
        return address_from_geo(lat, lng)


class FuzzyMultiPolygon(FuzzyText):
    def fuzz(self):
        pos = {'top': random.uniform(TOP, BOTTOM), 'left': random.uniform(LEFT, RIGHT), 'bottom': random.uniform(TOP, BOTTOM), 'right': random.uniform(LEFT, RIGHT)}
        return 'MULTIPOLYGON (((%(left)s %(top)s, %(left)s %(bottom)s, %(right)s %(bottom)s, %(right)s %(top)s, %(left)s %(top)s)))' % pos


class FuzzyPrice(BaseFuzzyAttribute):
    """Random integer within a given range."""

    def __init__(self, low, high=None, step=1, **kwargs):
        if high is None:
            high = low
            low = 0

        self.low = low
        self.high = high
        self.step = step

        super(FuzzyPrice, self).__init__(**kwargs)

    def fuzz(self):
        return random.randrange(self.low, self.high + 1, self.step) * 1000

class UserFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: "user%s" % n)
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)
    #main_group = factory.SubFactory('ads.factories.AccountFactory')

    @classmethod
    def _prepare(cls, create, password=None, **kwargs):
        return super(UserFactory, cls)._prepare(
            create,
            password=make_password(password),
            **kwargs
        )


class AccountFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = UserProfile
    user = factory.SubFactory(UserFactory)
    phone = '666 667'


class BaseFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = 'ads.BaseModel'
    ABSTRACT_FACTORY = True

    description = FuzzyText(length=200, chars=string.ascii_letters+' ')
    user = factory.SubFactory(UserFactory)

class AdFactory(BaseFactory):
    FACTORY_FOR = 'ads.Ad'

    location = FuzzyPoint()
    #address = FuzzyChoice(choices=["13 place d'Aligre, Paris", "22 rue esquirol, Paris"])
    address = FuzzyAddress()
    price = FuzzyPrice(10, 5000)
    habitation_type = FuzzyChoice(choices=[house, apartment])
    surface = FuzzyInteger(8, 180)
    surface_carrez = FuzzyInteger(8, 450)
    rooms = FuzzyInteger(1, 15)
    bedrooms = FuzzyInteger(1, 7)
    energy_consumption = FuzzyChoice(choices=FUZZY_ENERGY_CONSUMPTION_CHOICES)
    ad_valorem_tax = FuzzyInteger(100, 3000)
    housing_tax = FuzzyInteger(100, 3000)
    maintenance_charges = FuzzyInteger(100, 3000)
    emission_of_greenhouse_gases = FuzzyChoice(choices=FUZZY_EMISSION_OF_GREENHOUSE_GASES_CHOICES)
    ground_surface = FuzzyInteger(0, 3000)
    floor = FuzzyInteger(0, 30)
    ground_floor = FuzzyChoice(choices=[True, False])
    top_floor = FuzzyChoice(choices=[True, False])
    not_overlooked = FuzzyChoice(choices=[True, False])
    elevator = FuzzyChoice(choices=[True, False])
    intercom = FuzzyChoice(choices=[True, False])
    digicode = FuzzyChoice(choices=[True, False])
    doorman = FuzzyChoice(choices=[True, False])
    heating = FuzzyChoice(choices=FUZZY_HEATING_CHOICES)
    kitchen = FuzzyChoice(choices=[True, False])
    duplex = FuzzyChoice(choices=[True, False])
    swimming_pool = FuzzyChoice(choices=[True, False])
    alarm = FuzzyChoice(choices=[True, False])
    air_conditioning = FuzzyChoice(choices=[True, False])
    fireplace = FuzzyChoice(choices=FUZZY_FIREPLACE_CHOICES)
    terrace = FuzzyInteger(8, 50)
    balcony = FuzzyInteger(2, 20)
    separate_dining_room = FuzzyChoice(choices=[True, False])
    separate_toilet = FuzzyInteger(0, 4)
    bathroom = FuzzyInteger(0, 2)
    shower = FuzzyInteger(0, 2)
    separate_entrance = FuzzyChoice(choices=[True, False])
    cellar = FuzzyChoice(choices=[True, False])
    parking = FuzzyChoice(choices=FUZZY_PARKING_CHOICES)
    orientation =  FuzzyChoice(choices=['sud', 'sud-est', 'sud-ouest', 'nord', 'nord-ouest', 'nord-est'])


class SearchFactory(BaseFactory):
    FACTORY_FOR = 'ads.Search'

    location = FuzzyMultiPolygon()
    #price_min = FuzzyInteger(1, 5000000)
    price_max = FuzzyInteger(10000, 50000000)
    #habitation_types = FuzzyChoice(choices=[house, apartment])
    surface_min = FuzzyInteger(8, 300)
    #surface_max = FuzzyInteger(8, 1300)
    #rooms_min = FuzzyInteger(1, 10)
    #rooms_max = FuzzyInteger(1, 20)
    #bedrooms_min = FuzzyInteger(1, 10)
    #bedrooms_max = FuzzyInteger(3, 10)

    @factory.post_generation
    def habitation_types(self, create, extracted, **kwargs):
        #t = FuzzyChoice(choices=[house, apartment]).fuzz()
        #self.habitation_types.add(t)
        if not create:
            return
        if extracted:
            for habitation_type in extracted:
                self.habitation_types.add(habitation_type)
        else:
            t = FuzzyChoice(choices=[house, apartment]).fuzz()
            self.habitation_types.add(t)

