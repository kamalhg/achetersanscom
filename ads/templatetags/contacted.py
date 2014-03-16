from ads.models import Ad, Search, AdSearchRelation

from django import template
register = template.Library()

@register.filter(name='contacted')
def contacted(user, obj):
    if obj.__class__ == Ad:
        asr = AdSearchRelation.objects.filter(ad=obj, search__user=user).values_list('ad_contacted', flat=True)
        if any(asr):
            return True
        return False

    if obj.__class__ == Search:
        asr = AdSearchRelation.objects.filter(search=obj, ad__user=user).values_list('search_contacted', flat=True)
        if any(asr):
            return True
        return False
