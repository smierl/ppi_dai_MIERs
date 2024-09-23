"""
URL configuration for appPPI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views
from appPPI.views import index, logIn, privacidad, entrada, imc, mapa, ejercicios, change_password,password_change_done, estadisticas

urlpatterns = [
    path("admin/", admin.site.urls),
    path("index/", index),
    path("imc/", imc),
    path("mapa/", mapa),
    path("logIn/", logIn),
    path("privacidad/", privacidad),
    path("entrada/", entrada, name='entrada'),
    path('ejercicios/', ejercicios),
    path('estadisticas/', estadisticas, name="estadisticas"),
    path("accounts/", include("django.contrib.auth.urls")),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', change_password, name='change_password'),
    path('password_change/done/', password_change_done, name='password_change_done'),
]
