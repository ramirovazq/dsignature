# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from creacion_firma.utils import build_token
from creacion_firma.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in User.objects.all():
            token = build_token(user.curp, user.number_user)
            user.token = token
            user.save()
            print(user.username, token)
