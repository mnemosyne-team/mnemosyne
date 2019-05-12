from datetime import date, timedelta
import json
import random

from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, FormView, DetailView, UpdateView, View, ListView, DeleteView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import (
    JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
)

from wordbuilder.models import Dictionary, Word, Sense, UserWord, WordSet, Category, Statistics
from wordbuilder.utils import get_word_data, get_text, convert_image
from wordbuilder.forms import SignUpForm, ProfileUpdateForm, WordSetCreateForm, WordSetUpdateForm


class IndexView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        return redirect('dictionary/')


class SignUpView(FormView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        user = User.objects.get(username=form.cleaned_data['username'])
        Dictionary.objects.create(user=user)
        Statistics.objects.create(user=user)
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
    def get(self, request, word_set_pk):
        response = {'words': []}
        if word_set_pk == 0:
            words = request.user.dictionary.words.all()
        else:
            words = request.user.dictionary.words.filter(word_set__pk=word_set_pk).all()

        words = list(words)
        k = 10 if len(words) >= 10 else len(words)
        for word in random.sample(words, k=k):
            response['words'].append(word.to_dict())

        return JsonResponse(response, status=200)

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


class WordSetView(UserPassesTestMixin, ListView):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect(reverse('index'))

    model = WordSet
    template_name = 'wordbuilder/word_set.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        context['wordsets'] = dict()

        for wordset in WordSet.objects.all():
            words_count = UserWord.objects.filter(
                word_set=wordset
            ).distinct('word__name', 'sense__definitions__text').order_by().count()
            context['wordsets'][wordset] = words_count

        return context


class WordSetCreateView(UserPassesTestMixin, FormView):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect(reverse('index'))

    form_class = WordSetCreateForm
    template_name = 'wordbuilder/word_set_create.html'
    success_url = reverse_lazy('wordsets')

    def get_form_kwargs(self):
        kwargs = super(WordSetCreateView, self).get_form_kwargs()

        if self.request.method == 'GET':
            kwargs.update({
                'user': self.request.user,
            })
        return kwargs

    def form_valid(self, form):
        try:
            category = Category.objects.get(name=form.data.get('category'))
        except Category.DoesNotExist:
            category = Category(
                name=form.data.get('category')
            )
            category.save()

        image = self.request.FILES.get('image', None)

        if image is not None:
            x = form.cleaned_data.get('x')
            y = form.cleaned_data.get('y')
            width = form.cleaned_data.get('width')
            height = form.cleaned_data.get('height')
            img = convert_image(image, x, y, width, height)
        else:
            img = None

        wordset = WordSet(
            title=form.data.get('title'),
            category_id=category.id,
            image=img
        )
        wordset.save()

        for word_id in form.data.getlist('words'):
            word = UserWord.objects.get(id=word_id)
            word.word_set_id = wordset.id
            word.save()

        return redirect(self.success_url)


class CatalogView(LoginRequiredMixin, TemplateView):
    template_name = 'wordbuilder/collection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = dict()

        for category in Category.objects.all():
            if WordSet.objects.filter(category=category):
                context['categories'][category] = []
                for wordset in WordSet.objects.filter(category=category):
                    words_amount = UserWord.objects.filter(word_set=wordset).distinct().values_list('word_id').count()
                    context['categories'][category].append((wordset, words_amount))

        return context


class WordSetDetailView(LoginRequiredMixin, FormView):
    def get(self, request, word_set_id, **kwargs):
        words = UserWord.objects.filter(word_set_id=word_set_id).distinct('word__name', 'sense__definitions').order_by()

        user_has_words = UserWord.objects.filter(
            dictionary__user__username=request.user.username,
            word_set_id=word_set_id
        )

        user_words_names = user_has_words.values_list('word__name', flat=True)
        user_words_senses = user_has_words.values_list('sense__definitions__text', flat=True)

        word_set = WordSet.objects.get(id=word_set_id)

        return render(
            request,
            'wordbuilder/word_set_words.html',
            context={
                'user_own_words': user_has_words,
                'user_words_names': user_words_names,
                'user_words_senses': user_words_senses,
                'wordset_words': words,
                'wordset': word_set
            }
        )

    def post(self, request, word_set_id):
        word_list = request.POST.getlist('choices')
        user = request.user
        user_dict = Dictionary.objects.get(user__username=user.username)
        original_words = UserWord.objects.filter(pk__in=word_list)

        for word in original_words:
            new_word = UserWord(
                study_progress=0,
                dictionary=user_dict,
                lexical_category=word.lexical_category,
                pronunciation=word.pronunciation,
                sense=word.sense,
                word=word.word,
                word_set_id=word_set_id
            )
            new_word.save()

        return redirect(reverse_lazy('wordset_detail', kwargs={'word_set_id': word_set_id}))


class WordSetUpdateView(UserPassesTestMixin, FormView):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect(reverse('dictionary'))

    def get_form_kwargs(self):
        kwargs = super(WordSetUpdateView, self).get_form_kwargs()

        kwargs.update({
            'user': self.request.user,
            'word_set_id': self.kwargs['word_set_id']
        })
        return kwargs

    def form_valid(self, form):
        word_set_id = self.kwargs.pop('word_set_id', None)
        wordset = WordSet.objects.get(id=word_set_id)
        wordset.title = form.cleaned_data['title']

        if 'image' in self.request.FILES:
            image = self.request.FILES.get('image', None)
            x = form.cleaned_data.get('x')
            y = form.cleaned_data.get('y')
            width = form.cleaned_data.get('width')
            height = form.cleaned_data.get('height')

            img = convert_image(image, x, y, width, height)
            wordset.image = img

        try:
            new_category = Category.objects.get(name=form.cleaned_data['category'])
        except Category.DoesNotExist:
            new_category = Category.objects.create(name=form.cleaned_data['category'])

        wordset.category = new_category
        wordset.save()

        original_words = UserWord.objects.filter(word_set_id=word_set_id)
        original_words.update(word_set_id=None)

        new_words = form.cleaned_data['words']

        for word in new_words:
            multiple_words = UserWord.objects.filter(
                word__name=word.word.name,
                sense=word.sense
            )
            multiple_words.update(word_set_id=word_set_id)
        return redirect(self.success_url)

    template_name = 'wordbuilder/word_set_update.html'
    pk_url_kwarg = 'word_set_id'
    form_class = WordSetUpdateForm
    success_url = reverse_lazy('wordsets')


class WordSetDeleteView(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect(reverse('dictionary'))

    def delete(self, request, *args, **kwargs):
        word_set_id = self.kwargs.pop('word_set_id')
        UserWord.objects.filter(word_set_id=word_set_id).update(word_set_id=None)
        WordSet.objects.get(id=word_set_id).delete()
        return redirect(self.success_url)

    model = WordSet
    pk_url_kwarg = 'word_set_id'
    template_name = 'wordbuilder/word_set_delete.html'
    success_url = reverse_lazy('wordsets')


class ProgressUpdateAjaxView(LoginRequiredMixin, View):
    def post(self, request):
        trained_words = json.loads(request.body.decode('utf-8')).get('words')
        for word in trained_words:
            user_word = self.request.user.dictionary.words.filter(
                word__name=word['word'].lower()
            ).first()

            if word['isSuccessfullyTrained'] and \
                    user_word.study_progress < 100:
                user_word.study_progress += 25
                if user_word.study_progress == 100:
                    user_word.learn_date = date.today()
                user_word.save()
            elif not word['isSuccessfullyTrained'] and user_word.study_progress > 0:
                user_word.study_progress -= 25
            user_word.save()
        return JsonResponse({}, status=200)


class TrainingsView(LoginRequiredMixin, TemplateView):
    template_name = 'wordbuilder/trainings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wordset_ids = self.request.user.dictionary.words.values_list('word_set', flat=True).filter(
            word_set__isnull=False
        ).order_by('word_set').distinct()
        wordsets = WordSet.objects.filter(pk__in=wordset_ids)
        context['wordsets'] = wordsets
        return context


class WordConstructorView(LoginRequiredMixin, TemplateView):
    template_name = 'wordbuilder/word_constructor.html'


class DefinitionsView(LoginRequiredMixin, TemplateView):
    template_name = 'wordbuilder/definitions_training.html'


class PronunciationView(LoginRequiredMixin, TemplateView):
    template_name = 'wordbuilder/pronunciation_training.html'

    def post(self, request, category):
        result = get_text(request.FILES['audio_data'])
        return JsonResponse(result, status=200)


class StatisticsView(TemplateView):
    template_name = 'wordbuilder/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username=self.request.user.username)
        user_stats = Statistics.objects.get(user=user)

        user_words = UserWord.objects.filter(dictionary__user=user, learn_date__isnull=False)

        learned_words = UserWord.objects.filter(dictionary__user=user, study_progress__exact=100).count()
        words_to_learn = UserWord.objects.filter(dictionary__user=user, study_progress__lt=100).count()

        weekly_words = []
        week_days = []
        for delta in range(7):
            weekly_words.append(
                user_words.filter(
                    learn_date=date.today() - timedelta(days=delta)
                ).count()
            )
            week_days.append(
                (date.today() - timedelta(days=delta)).strftime("%d %b %Y")
            )

        context['learned_words'] = learned_words
        context['words_to_learn'] = words_to_learn
        context['day_streak'] = user_stats.day_streak
        context['record_day_streak'] = user_stats.record_day_streak
        context['weekly_words'] = weekly_words
        context['week_days'] = week_days

        return context

      
def error_404(request, exception):
    return render(request, 'wordbuilder/errors/404.html', context={})


def error_500(request):
    return render(request, 'wordbuilder/errors/500.html', context={})


class ListeningTrainingView(LoginRequiredMixin, TemplateView):
    template_name = 'wordbuilder/training_listening.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = int(context['category'])
        if category == 0:
            user_words_sorted = sorted(
                self.request.user.dictionary.words.all(),
                key=lambda x: x.study_progress, reverse=False
            )
        else:
            user_words_sorted = sorted(
                self.request.user.dictionary.words.filter(
                    word_set_id=category
                ),
                key=lambda x: x.study_progress, reverse=False
            )
        words = [
            word for word in user_words_sorted
            if word.pronunciation is not None
        ]

        if len(user_words_sorted) < 10:
            context['words'] = words
        else:
            context['words'] = random.sample(words, 10)
        return context
