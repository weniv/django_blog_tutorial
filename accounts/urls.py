from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logindrf/', views.LoginViewDrf.as_view(), name='logindrf'),
]