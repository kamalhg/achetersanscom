from leaflet.admin import LeafletGeoAdmin

from django.contrib import admin
from .models import Ad, AdPicture, Search, HabitationType, AdSearchRelation

class AdSearchRelationAdmin(admin.ModelAdmin):
    list_display = ['id', 'ad', 'search', 'ad_contacted', 'search_contacted', 'ad_notified', 'search_notified', 'valid']


class AdAdmin(LeafletGeoAdmin):
    list_display = ['slug', 'price', 'surface' ]


class SearchAdmin(LeafletGeoAdmin):
    list_display = ['slug', 'price_max', 'surface_min', 'location', ]


admin.site.register(Ad, AdAdmin)
admin.site.register(AdPicture)
admin.site.register(HabitationType)
admin.site.register(Search, SearchAdmin)
admin.site.register(AdSearchRelation, AdSearchRelationAdmin)
