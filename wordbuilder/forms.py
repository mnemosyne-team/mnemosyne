from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


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
