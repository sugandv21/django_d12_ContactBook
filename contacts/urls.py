from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("add/", views.add_contact, name="add_contact"),
    path("feedback/", views.feedback, name="feedback"),
    path("signup/", views.signup, name="signup"),  
]