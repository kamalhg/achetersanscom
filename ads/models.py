#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis import geos
from django.db.models.signals import post_save, m2m_changed
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import AutoSlugField
from django.contrib.auth.models import User
from django.db.models import Q

from django.utils.translation import ugettext as _

from .utils import geo_from_address


class BaseModel(TimeStampedModel):
    description = models.TextField(_('description'), blank=True, null=True)
    user = models.ForeignKey(User)

    class Meta:
        abstract = True


ENERGY_CONSUMPTION_CHOICES = (
    ('A', _(u'A - ≤ 50')),
    ('B', _(u'B - 51 à 90')),
    ('C', _(u'C - 91 à 150')),
    ('D', _(u'D - 151 à 230')),
    ('E', _(u'E - 231 à 330')),
    ('F', _(u'F - 331 à 450')),
    ('G', _(u'G - > 450')),
)

EMISSION_OF_GREENHOUSE_GASES_CHOICES = (
    ('A', _(u'A - ≤ 5')),
    ('B', _(u'B - 6 à 10')),
    ('C', _(u'C - 11 à 20')),
    ('D', _(u'D - 21 à 35')),
    ('E', _(u'E - 36 à 55')),
    ('F', _(u'F - 56 à 80')),
    ('G', _(u'G - > 80')),
)

HEATING_CHOICES = (
    ('1', _(u'individuel gaz')),
    ('2', _(u'individuel électrique')),
    ('3', _(u'collectif gaz')),
    ('4', _(u'collectif fuel')),
    ('5', _(u'collectif réseau de chaleur')),
    ('13', _(u'autres'))
)


KITCHEN_CHOICES = (
    ('1', _(u'américaine')),
    ('2', _(u'séparée')),
    ('3', _(u'industrielle')),
    ('4', _(u'coin-cuisine')),
    ('5', _(u'belle vue')),
    ('6', _(u'sans vis à vis')),
    ('7', _(u'américaine équipée')),
    ('8', _(u'séparée équipée')),
    ('9', _(u'coin cuisine équipé')),
)


PARKING_CHOICES = (
    ('1', _(u'Place de parking')),
    ('2', _(u'Box fermé')),
)

FIREPLACE_CHOICES = (
    ('1', _(u'Foyer ouvert')),
    ('2', _(u'Insert')),
)

class HabitationType(models.Model):
    label = models.CharField(max_length=25)

    def __unicode__(self):
        return self.label

class Ad(BaseModel):
    """
    Ad model
    """
    slug = AutoSlugField(_('slug'), populate_from='slug_format')
    location = models.PointField()
    address = models.CharField(_(u"Adresse"), max_length=255)
    price = models.PositiveIntegerField(_(u"Prix"))
    habitation_type = models.ForeignKey(HabitationType, verbose_name="Type de bien")
    surface = models.IntegerField(_(u"Surface habitable"))
    surface_carrez = models.IntegerField(_(u"Surface Loi Carrez"),
                                         null=True, blank=True)
    rooms = models.PositiveIntegerField(_(u"Nombre de pièces"))
    bedrooms = models.PositiveIntegerField(_(u"Nombre de chambres"))
    energy_consumption = models.CharField(_(u"Consommation énergétique (kWhEP/m².an)"),
                                          max_length=1,
                                          choices=ENERGY_CONSUMPTION_CHOICES,
                                          null=True, blank=True)
    ad_valorem_tax = models.IntegerField(_(u'Taxe foncière'), null=True,
                                         blank=True,
                                         help_text=_(u"Montant annuel, sans espace, sans virgule"))
    housing_tax = models.IntegerField(_(u"Taxe d'habitation"), null=True,
                                      blank=True, help_text=_(u"Montant annuel, sans espace, sans virgule"))
    maintenance_charges = models.IntegerField(_(u'Charges'), null=True,
                                              blank=True, help_text=_(u"Montant mensuel, sans espace, sans virgule"))
    emission_of_greenhouse_gases = models.CharField(_(u"Émissions de gaz à effet de serre (kgeqCO2/m².an)"),
                                                    max_length=1,
                                                    choices=EMISSION_OF_GREENHOUSE_GASES_CHOICES,
                                                    null=True, blank=True)
    ground_surface = models.IntegerField(_(u'Surface du terrain'),
                                       null=True, blank=True)
    floor = models.PositiveIntegerField(_(u'Etage'), null=True, blank=True)
    ground_floor = models.BooleanField(_(u'Rez de chaussé'))
    top_floor = models.BooleanField(_(u'Dernier étage'))
    not_overlooked = models.BooleanField(_(u'Sans vis-à-vis'))
    elevator = models.BooleanField(_(u"Ascenceur"))
    intercom = models.BooleanField(_(u"Interphone"))
    digicode = models.BooleanField(_(u"Digicode"))
    doorman = models.BooleanField(_(u"Gardien"))
    heating = models.CharField(_(u"Chauffage"), max_length=2,
                               choices=HEATING_CHOICES, null=True, blank=True)
    kitchen = models.BooleanField(_(u"Cuisine équipée"))
    duplex = models.BooleanField(_(u"Duplex"))
    swimming_pool = models.BooleanField(_(u"Piscine"))
    alarm = models.BooleanField(_(u"Alarme"))
    air_conditioning = models.BooleanField(_(u"Climatisation"))
    fireplace = models.CharField(_(u"Cheminée"), max_length=2,
                               choices=FIREPLACE_CHOICES, null=True, blank=True)
    terrace = models.IntegerField(_(u"Terrasse"), null=True, blank=True)
    balcony = models.IntegerField(_(u"Balcon"), null=True, blank=True)
    separate_dining_room = models.BooleanField(_(u"Cuisine séparée"))
    separate_toilet = models.IntegerField(_(u"Toilettes séparés"), null=True, blank=True)
    bathroom = models.IntegerField(_(u"Salle de bain"), null=True, blank=True)
    shower = models.IntegerField(_(u"Salle d'eau (douche)"), null=True, blank=True)
    separate_entrance = models.BooleanField(_(u"Entrée séparée"))
    cellar = models.BooleanField(_(u"Cave"))
    parking = models.CharField(_(u"Parking"), max_length=2,
                               choices=PARKING_CHOICES, null=True, blank=True)
    orientation = models.CharField(_(u"Orientation"), max_length=255, null=True, blank=True)

    objects = models.GeoManager()

    @models.permalink
    def get_absolute_url(self):
        return ('ads_ad_detail', [str(self.slug)])

    def save(self, *args, **kwargs):
        print kwargs
        print args
        self.location = geo_from_address(self.address)
        #self.my_stuff = 'something I want to save in that field'
        super(Ad, self).save(*args, **kwargs)

    def _get_slug_format(self):
        return u'%s-%se-%sm²' % (self.habitation_type.label, self.price, self.surface)
    slug_format = property(_get_slug_format)


    def _get_search_query(self):
        return '?price_max=%s&surface_min=%s&location=%s' % (self.price, self.surface, geos.MultiPolygon(self.location.buffer(0.015)))

    search_query = property(_get_search_query)

    def __unicode__(self):
        return u'%s - %s € - %s m²' % (self.habitation_type.label, self.price, self.surface)


class AdPicture(models.Model):
    """
    Ad Picture model
    """
    ad = models.ForeignKey(Ad)
    image = models.ImageField("Photo", upload_to="pictures/%Y/%m/%d")
    title = models.CharField("Titre", max_length=255, null=True, blank=True)


class Search(BaseModel):
    """
    Search model
    """
    slug = AutoSlugField(_('slug'), populate_from='slug_format')
    location = models.MultiPolygonField()
    #price_min = models.PositiveIntegerField(_(u"Prix min"), null=True, blank=True)
    price_max = models.PositiveIntegerField(_(u"Prix max"))
    #habitation_types = models.CharField(_(u"Type de bien"), max_length=1,
    #                                   choices=HABITATION_TYPE_CHOICES, null=True, blank=True)
    habitation_types = models.ManyToManyField(HabitationType)
    surface_min = models.PositiveIntegerField(_(u"Surface min"))
    #surface_max = models.PositiveIntegerField(_(u"Surface max"), null=True, blank=True)
    #rooms_min = models.PositiveIntegerField(_(u"Nb de pièce min"), null=True, blank=True)
    #rooms_max = models.PositiveIntegerField(_(u"Nb de pièce max"), null=True, blank=True)
    #bedrooms_min = models.PositiveIntegerField(_(u"Nb de chambres min"), null=True, blank=True)
    #bedrooms_max = models.PositiveIntegerField(_(u"Nb de chambres min"), null=True, blank=True)

    objects = models.GeoManager()

    @models.permalink
    def get_absolute_url(self):
        return ('ads_search_detail', [str(self.slug)])

    def _get_slug_format(self):
        return u'%se-max-%sm²-min' % (self.price_max, self.surface_min)
    slug_format = property(_get_slug_format)

    def __unicode__(self):
        return u'%s - %s € max. - %s m² min.' % (', '.join(self.habitation_types.all().values_list('label', flat=True)), self.price_max, self.surface_min)


class AdSearchRelation(TimeStampedModel):
    """
    Ad Search model Relation
    """
    ad = models.ForeignKey(Ad)
    search = models.ForeignKey(Search)
    ad_notified = models.DateTimeField(null=True, blank=True)
    search_notified = models.DateTimeField(null=True, blank=True)
    ad_contacted = models.DateTimeField(null=True, blank=True)
    search_contacted =  models.DateTimeField(null=True, blank=True)
    valid = models.BooleanField()

    def has_vendor_contacted_buyer_for_search(self, vendor, search):
        pass

    def has_buyer_contacted_vendor_for_ad(self, buyer, ad):
        pass

    class Meta:
        unique_together = (('ad', 'search'), )

    def save(self, *args, **kwargs):
        if not self.pk:
            # We notify owner and searchers
            pass
        super(AdSearchRelation, self).save(*args, **kwargs)


def update_adsearch_relation_from_ad(sender, instance, **kwargs):
    ad = instance
    s = Search.objects\
            .filter(Q(price_max__gte=ad.price) | Q(price_max=None))\
            .filter(Q(surface_min__lte=ad.surface) | Q(surface_min=None))\
            .filter(Q(habitation_types=ad.habitation_type) | Q(habitation_types=None))\
            .filter(Q(location__contains=ad.location) | Q(location=None))
            #.filter(Q(price__min__lte=ad.price) | Q(price__min=None))\
            #.filter(Q(surface_max__gte=ad.surface) | Q(surface_max=None))\
            #.filter(Q(rooms_min__lte=ad.rooms) | Q(rooms_moin=None))\
            #.filter(Q(rooms_max__gte=ad.rooms) | Q(rooms_max=None))\
            #.filter(Q(bedrooms_min__lte=ad.bedrooms) | Q(bedrooms_min=None))\
            #.filter(Q(bedrooms_max__gte=ad.bedrooms) | Q(bedrooms_max=None))\

    asr = AdSearchRelation.objects.filter(ad=ad).values_list('search', flat=True)
    #search in s and not in asr => add
    for search in s:
        if search not in asr:
            a = AdSearchRelation(ad=ad, search=search, valid=True)
            a.save()
    #search in s and in asr => nothing
    for search in asr:
        if search in s:
            a = AdSearchRelation.objects.get(ad=ad, search=search)
            a.valid = True
            a.save()
        else:
            a = AdSearchRelation.objects.get(ad=ad, search=search)
            a.valid = False
            a.save()

def update_adsearch_relation_from_search(sender, instance, **kwargs):
    search = instance
    q_ad = Ad.objects.all().filter(price__lte=search.price_max)\
                           .filter(surface__gte=search.surface_min)\
                           .filter(habitation_type__in=search.habitation_types.all())\
                           .filter(location__within=search.location)
    asr = AdSearchRelation.objects.filter(search=search).values_list('ad', flat=True)
    for ad in asr:
        if ad not in q_ad:
            a = AdSearchRelation.objects.get(ad=ad, search=search)
            a.valid = False
        else:
            a = AdSearchRelation.objects.get(ad=ad, search=search)
            a.valid = True
        a.save()
    for ad in q_ad:
        if ad not in asr:
            a = AdSearchRelation(ad=ad, search=search, valid=True)
            try:
                a.save()
            except:
                print 'save just in above for loop'

post_save.connect(update_adsearch_relation_from_ad, sender=Ad)
post_save.connect(update_adsearch_relation_from_search, sender=Search)

m2m_changed.connect(update_adsearch_relation_from_search, sender=Search.habitation_types.through)
