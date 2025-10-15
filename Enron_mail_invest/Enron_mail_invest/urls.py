"""
URL configuration for Enron_mail_invest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mail_form import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='home'),
    path('query1/', views.query1, name='query1'),
    path('query2/', views.query2, name='query2'),
    path('query3/', views.query3, name='query3'),
    path('query4/', views.query4, name='query4'),
    path('query5/', views.query5, name='query5'),
    path('query6/', views.query6, name='query6'),
    path('query7/', views.query7, name='query7'),
    path('queryresult7/', views.queryresult7, name='queryresult7'),
    path('requete/', views.requete, name='requete'),
]

