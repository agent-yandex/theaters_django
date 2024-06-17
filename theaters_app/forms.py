"""Module for defining forms used in the Django project."""

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import CharField, DecimalField, Form

from .config import MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS


class RegistrationForm(UserCreationForm):
    """Form for user registration with username, first name, last name, email and password."""

    first_name = CharField(max_length=100, required=True)
    last_name = CharField(max_length=100, required=True)
    email = CharField(max_length=100, required=True)

    class Meta:
        """Meta class specifying the model and fields to be included in the form."""

        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class AddFundsForm(Form):
    """A form for adding funds to a user's account."""

    money = DecimalField(
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
    )

    def is_valid(self) -> bool:
        """
        Validate the form, ensuring that the money field is specified and positive.

        Returns:
            bool: True if the form is valid, False otherwise.
        """
        is_valid = super().is_valid()
        if not is_valid:
            return False
        money = self.cleaned_data.get('money', None)
        if not money:
            self.add_error(
                'money',
                ValidationError('an error occured, money field was not specified!'),
            )
            return False
        if money <= 0:
            self.add_error(
                'money',
                ValidationError('you can only add positive amount of money!'),
            )
            return False
        return True
