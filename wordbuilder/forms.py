from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.db.models import Q
from django.forms import CheckboxSelectMultiple

from wordbuilder.models import UserWord, WordSet


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=75, required=True)
    first_name = forms.CharField(max_length=75, required=True)
    last_name = forms.CharField(max_length=75, required=True)

    error_messages = {
        'email_taken': "The email you entered is already taken.",
        'password_mismatch': "The passwords you have entered are not identical."
    }

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_email(self):
        """
        Checks whether user with given email already exists.
        """
        email = self.cleaned_data["email"]

        try:
            User.objects.get(email=email)
            raise forms.ValidationError(
                self.error_messages['email_taken'],
                code='email_taken',
            )
        except User.DoesNotExist:
            return email


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(max_length=75, required=True)
    first_name = forms.CharField(max_length=75, required=True)
    last_name = forms.CharField(max_length=75, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class WordSetCreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['words'] = forms.ModelMultipleChoiceField(
                required=True,
                widget=CheckboxSelectMultiple,
                label='Words',
                queryset=UserWord.objects.filter(
                    dictionary__user_id=user.id, word_set__isnull=True
                )
            )

    title = forms.CharField(max_length=30, required=True, label='Title')
    category = forms.CharField(max_length=30, required=True, label='Category')
    image = forms.ImageField(label='Image', required=False)
    x = forms.FloatField(widget=forms.HiddenInput(), label='SizeX', required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), label='SizeY', required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), label='SizeWidth', required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), label='SizeHeight', required=False)


class WordSetUpdateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        word_set = WordSet.objects.get(id=kwargs.pop('word_set_id', None))

        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['title'] = forms.CharField(
                max_length=30,
                required=True,
                label='Title',
                initial=word_set.title
            )
            self.fields['category'] = forms.CharField(
                max_length=30,
                required=True,
                label='Category',
                initial=word_set.category.name
            )
            self.fields['image'] = forms.ImageField(
                initial=word_set.image,
                label='Image',
                required=False
            )
            self.fields['words'] = forms.ModelMultipleChoiceField(
                required=False,
                widget=CheckboxSelectMultiple,
                label='Words',
                queryset=UserWord.objects.filter(
                    Q(dictionary__user_id=user.id, word_set__isnull=True) | Q(word_set=word_set)
                ).distinct('word__name', 'sense').order_by()
            )
            self.fields['x'] = forms.FloatField(widget=forms.HiddenInput(), label='SizeX', required=False)
            self.fields['y'] = forms.FloatField(widget=forms.HiddenInput(), label='SizeY', required=False)
            self.fields['width'] = forms.FloatField(widget=forms.HiddenInput(), label='SizeWidth', required=False)
            self.fields['height'] = forms.FloatField(widget=forms.HiddenInput(), label='SizeHeight', required=False)
