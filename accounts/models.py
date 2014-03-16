#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    phone = models.CharField(u'Téléphone', max_length=255)

    @models.permalink
    def get_absolute_url(self):
        return ('user_account', [str(self.user.username)])

    def __unicode__(self):
        return self.user.username
