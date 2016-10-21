# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from creacion_firma.models import FirmarCertificado, NominaSubida, User

import datetime

class UserForm(forms.Form):
    nombre = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"style": "width: 400px"}))
    correo_electronico = forms.EmailField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class FirmarCertificadoForm(ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        required=True)

    class Meta:
        model = FirmarCertificado
        exclude = ('certificado',)


class SubirNominaForm(forms.Form):
    anteriores = forms.ModelChoiceField(
        queryset=NominaSubida.objects.filter(visible=True),
        required=False)
    nombre = forms.CharField(
        max_length=50, 
        widget=forms.TextInput(attrs={"style": "width: 150px"}),
        help_text="QNA, Reyes, etc",
        required=False)
    numero = forms.IntegerField(required=False)
    year = forms.IntegerField(label=u"Año", required=False)
    tipo = forms.ChoiceField(choices=(("ord", "Ordinaria"), ("ext", "Extraordinaria")), required=False)
    pdf = forms.FileField()
    xml = forms.FileField()

    def clean(self):
        cleaned_data = super(SubirNominaForm, self).clean()
        anteriores_nomina = cleaned_data.get("anteriores")
        nomina = cleaned_data.get("nombre")

        if not (anteriores_nomina or nomina):
            msg = "Elija un nombre o escriba uno"
            self.add_error('anteriores', msg)
            self.add_error('nombre', msg)


class SubirNominaXMLForm(forms.Form):
    anteriores = forms.ModelChoiceField(
        queryset=NominaSubida.objects.filter(visible=True),
        required=False)
    nombre = forms.CharField(
        max_length=50, 
        widget=forms.TextInput(attrs={"style": "width: 150px"}),
        help_text="QNA, Reyes, etc",
        required=False)
    numero = forms.IntegerField(required=False)
    year = forms.IntegerField(label=u"Año", required=False)
    tipo = forms.ChoiceField(choices=(("ord", "Ordinaria"), ("ext", "Extraordinaria")), required=False)
    xml = forms.FileField()

    def clean(self):
        cleaned_data = super(SubirNominaXMLForm, self).clean()
        anteriores_nomina = cleaned_data.get("anteriores")
        nomina = cleaned_data.get("nombre")

        if not (anteriores_nomina or nomina):
            msg = "Elija un nombre o escriba uno"
            self.add_error('anteriores', msg)
            self.add_error('nombre', msg)


class LoginForm(forms.Form):
    usuario = forms.CharField(max_length=150)
    password = forms.CharField(max_length=32, widget=forms.PasswordInput) 

class SelectYearForm(forms.Form):
    year = forms.ChoiceField(label="Año", choices=((y, y) for y in xrange(2015, 2020)))

class FirmaOSinForm(forms.Form):
    tipo = forms.ChoiceField(label="Tipo", choices=(("f", "firmado"), ("nf", "no firmado")))

class NominasFilterYear(forms.Form):
    def __init__(self, *args, **kwargs):
        if "year" in kwargs:
            self.year = kwargs["year"]
            del kwargs["year"]
        else:
            self.year = datetime.date.today().year
        super(NominasFilterYear, self).__init__(*args, **kwargs)

        self.fields['nomina'] = forms.ModelChoiceField(
            queryset=NominaSubida.objects.filter(year=self.year).order_by("-numero", "nombre", "tipo")
        )

