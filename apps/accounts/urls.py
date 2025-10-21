from django.urls import path
from django.contrib.auth import views as auth_views

from .views import RegisterView, CustomLoginView, CustomLogoutView, ProfileView, ProfileUpdateView, \
    CustomPasswordChangeView, email_subscribe


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('email/', email_subscribe, name='email'),
]
