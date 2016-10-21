from django.contrib import admin

# Register your models here.
from django.contrib import admin
from creacion_firma import models

class UserAdmin(admin.ModelAdmin):
    list_display = ['username']
    search_fields = ['username']

class UserDocumentSignAdmin(admin.ModelAdmin):
    list_display = ['user', 'nomina']
    search_fields = ['user__username']

class TransactionStatusAdmin(admin.ModelAdmin):
    list_filter = ['status']

class NominaSubidaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'numero', 'year', 'tipo', 'visible', 'fecha']

admin.site.register(models.User, UserAdmin)  
admin.site.register(models.UserDocumentSign, UserDocumentSignAdmin)
admin.site.register(models.Certificado)
admin.site.register(models.TransactionStatus, TransactionStatusAdmin)
admin.site.register(models.NominaSubida, NominaSubidaAdmin)
