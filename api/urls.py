from django.urls import path

from . import views

urlpatterns = [
    path('', views.home),
    path('pdf/<slug:base64_string>/', views.pdf),
]
