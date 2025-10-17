from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, UpdateView, TemplateView

from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from .models import CustomUser



class RegisterView(SuccessMessageMixin, CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('index')
    success_message = 'Регистрация прошла успешно! Добро пожаловать!'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # автоматический вход после регистрации
        return response


class CustomLoginView(SuccessMessageMixin, LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    success_message = 'Добро пожаловать!'
    success_url = reverse_lazy('index')

    # def get_success_url(self):
    #     return self.request.GET.get('next', reverse_lazy('home'))  # редирект на next или home


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('index')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('profile')
    success_message = 'Профиль успешно обновлен!'

    def get_object(self, queryset=None):
        return self.request.user


class CustomPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('profile')
    success_message = 'Пароль успешно изменен!'
