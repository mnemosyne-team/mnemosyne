from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, DetailView, UpdateView
from django.contrib.auth.models import User

from wordbuilder.forms import SignUpForm, ProfileUpdateForm
from .models import Dictionary


class IndexView(TemplateView):
    template_name = 'wordbuilder/index.html'


class SignUpView(FormView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        user = User.objects.get(username=form.cleaned_data['username'])
        Dictionary.objects.create(user=user)
        return redirect(self.success_url)


class DictionaryView(TemplateView):
    template_name = 'wordbuilder/dictionary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['words'] = self.request.user.dictionary.words.all()
        return context


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'wordbuilder/profile-view.html'

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'wordbuilder/profile-update-view.html'
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        if form.cleaned_data['email'] in \
                [i.email for i in User.objects.exclude(id=self.get_object().id)]:
            form.add_error('email', 'User with this email already exists')
            return self.form_invalid(form)
        return super(ProfileUpdateView, self).form_valid(form)
