from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, UpdateView, TemplateView




from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm, EmailSubscribeForm
from .models import CustomUser



class RegisterView(SuccessMessageMixin, CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('index')
    success_message = 'Регистрация прошла успешно! Добро пожаловать!'

    def form_valid(self, form):
        response = super().form_valid(form)
        inactive_user = send_verification_email(self.request, form)
        login(self.request, self.object)  # автоматический вход после регистрации
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context


class CustomLoginView(SuccessMessageMixin, LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    success_message = 'Добро пожаловать!'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход в систему'

        return context

    # def get_success_url(self):
    #     return self.request.GET.get('next', reverse_lazy('home'))  # редирект на next или home


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('index')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Профиль'
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование профиля'

        return context


class CustomPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('profile')
    success_message = 'Пароль успешно изменен!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменение пароля'

        return context


def email_subscribe(request):

    if request.method == 'POST':
        form = EmailSubscribeForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            subject = "Оптово-розничный интернет-магазин."
            message = 'Вы успешно подписались на нашу рассылку!'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [cd['email']])
            return redirect('index')
    else:
        form = EmailSubscribeForm()
    # print(form)

    # return render(request, 'email_subscribe.html', {'form': form})
    return render(request, 'base.html', {'form': form})
