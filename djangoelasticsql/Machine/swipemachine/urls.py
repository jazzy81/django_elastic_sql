"""
URL configuration for Machine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from swipemachine import views

# urlpatterns = [ 
#     path("", views.index,name= "home"),
#     path("about", views.about,name="about"),
#     path("login/", views.login, name="login"),
#     path("dashboard/", views.dashboard, name="dashboard"),
#     path("deposit/", views.deposit, name="deposit"),
#     path("withdraw/", views.withdraw, name="withdraw"),
#     path("logout/", views.logout_view, name="logout"),
#     path("services/signup",views.services_sign_up,name="services"),
#     path("contact",views.contact,name="contact")
# ]

urlpatterns = [
    path("", views.index, name="home"),
    # path("about", views.about, name="about"),
    path("services/login", views.login, name="login"), 
    path("withdraw/<str:card_no>/", views.withdraw, name="withdraw"),  # Withdraw
    path("deposit/<str:card_no>/", views.deposit, name="deposit"), 
    path("logout/", views.logout, name="logout"),
    
]
