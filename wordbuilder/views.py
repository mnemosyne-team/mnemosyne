from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.contrib.auth.models import User

from wordbuilder.forms import SignUpForm
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
