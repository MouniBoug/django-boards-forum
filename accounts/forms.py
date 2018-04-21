# email address field is missing. the UserCreationForm does not provide an email field. But we can extend it.
# so we use the following class we're creating that's inherting from UserCreationForm class in our views.py
# instead of UserCreationForm

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):  # SignUpForm extends the UserCreationForm
    email = forms.CharField(
        widget=forms.EmailInput(),
        max_length=254,
        required=True,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
