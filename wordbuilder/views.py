import json

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, DetailView, UpdateView, View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
)

from wordbuilder.models import Dictionary, Word, Sense, UserWord
from wordbuilder.utils import get_word_data
from wordbuilder.forms import SignUpForm, ProfileUpdateForm


class IndexView(LoginRequiredMixin, TemplateView):
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


class DictionaryView(LoginRequiredMixin, TemplateView):
    template_name = 'wordbuilder/dictionary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['words'] = self.request.user.dictionary.words.all()
        return context


class WordDataView(LoginRequiredMixin, View):
    def get(self, request, word):
        word = word.lower()
        word_obj = Word.objects.filter(name=word).first()
        if word_obj:
            word_dict = word_obj.to_dict()
        else:
            word_data = get_word_data(word)
            if word_data:
                word_obj = Word.from_dict(word_data)
                word_dict = word_obj.to_dict()
            else:
                return HttpResponseNotFound()

        return JsonResponse(word_dict)


class UserWordView(LoginRequiredMixin, View):
    def post(self, request):
        sense_id = request.POST.get('sense')
        sense = Sense.objects.get(pk=sense_id) if sense_id else None
        if sense:
            pronunciation = sense.lexical_entry.pronunciation
            lexical_category = sense.lexical_entry.lexical_category
            word = sense.lexical_entry.word
            dictionary = self.request.user.dictionary

            user_word = UserWord(
                dictionary=dictionary, word=word,
                lexical_category=lexical_category,
                pronunciation=pronunciation, sense=sense
            )
            user_word.save()

        return redirect(reverse_lazy('dictionary'))

    def delete(self, request):
        try:
            data = request.body.decode('utf-8')
            json_data = json.loads(data)
            user_word_id = json_data.get('userWordId')
            user = request.user
            Dictionary.objects.get(user=user).words.filter(pk=user_word_id).delete()
            return HttpResponse(status=204)
        except Exception as e:
            return HttpResponseBadRequest()
          
          
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


class ProgressUpdateAjaxView(LoginRequiredMixin, TemplateView):
    template_name = None

    def post(self, request):
        trained_words = request.POST.get('successfully_trained')
        for word in trained_words:
            user_word = self.request.user.dictionary.words.filter(
                word__name=word
            ).first()
            if user_word.study_progress < 100:
                user_word.study_progress += 25
                user_word.save()
