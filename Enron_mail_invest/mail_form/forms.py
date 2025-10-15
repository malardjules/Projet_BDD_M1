#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 14:36:31 2024

@author: aze
"""

from django import forms


class Form1(forms.Form):
    option = forms.ChoiceField(label='Option de recherche', choices= [('lastname', 'Recherche par nom'), ('email', 'Recherche par email'),])
    fields_lastname = forms.CharField(label='Recherche par nom', required=False)
    fields_email = forms.CharField(label='Recherche par email', required=False)


class Form2(forms.Form):
    mailType = forms.ChoiceField(choices=[('sent', 'Envoyé'), ('received', 'Reçu'), ('both', 'Envoyé ou Reçu')])
    mailCountComparison = forms.ChoiceField(choices=[('more', 'Plus de'), ('less', 'Moins de')])
    mailCount = forms.IntegerField()
    startDate = forms.DateField()
    endDate = forms.DateField()
    exchangeType = forms.ChoiceField(choices=[('internal', 'Internes'), ('internal_external', 'Internes et Externes')])

    
    
class Form3(forms.Form):
    employeeID = forms.IntegerField()
    startDate = forms.DateField()
    endDate = forms.DateField()

class Form4(forms.Form):
    limitResult = forms.IntegerField()
    startDate = forms.DateField()
    endDate = forms.DateField()
    
class Form5(forms.Form):
    startDate = forms.DateField()
    endDate = forms.DateField()
    exchangeType = forms.ChoiceField(choices=[('internal', 'Internes'), ('internal_external', 'Internes et Externes')])
    
class Form6(forms.Form):
    sortType = forms.ChoiceField(choices=[('sender', 'Expéditeur'), ('subject', 'Sujet'),('date', 'Date')])
    keywords = forms.CharField(widget=forms.Textarea, required=False, help_text="Entrez les mots-clés séparés par des virgules.")

    def clean_keywords(self): #s'exécute automatiquement  à la réupération du mot 
        """ Nettoie et valide les mots-clés entrés par l'utilisateur. """
        keywords_raw = self.cleaned_data['keywords']
        # Sépare les mots-clés par des virgules, supprime les espaces inutiles et filtre les chaînes vides
        keyword_list = [keyword.strip() for keyword in keywords_raw.split(',') if keyword.strip()]
        return keyword_list
    
class Form7(forms.Form):
    option = forms.ChoiceField(label='Option de recherche', choices= [('id', 'Recherche par identifiant de l\'employee'), ('email', 'Recherche par email'),])
    fields_id = forms.CharField(label='Recherche par identifiant', required=False)
    fields_email = forms.CharField(label='Recherche par email', required=False)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    