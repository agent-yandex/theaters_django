"""This module defines the URL configuration for a Django web application."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('theaters_app.urls')),
]
