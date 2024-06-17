"""Module that tests forms."""

from django.contrib.auth.models import User
from django.test import TestCase

from theaters_app.config import MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS
from theaters_app.forms import AddFundsForm, RegistrationForm


class AddFundsFormTest(TestCase):
    """Test case for the RegistrationForm class."""

    def test_long_field(self):
        """Test case to validate the behavior of 'money' field with too many digits."""
        form = AddFundsForm(data={'money': int('9' * (MONEY_MAX_DIGITS + 1))})
        self.assertFalse(form.is_valid())

    def test_too_much_dp(self):
        """Test case to validate the behavior of 'money' field with too many decimal places."""
        dp = '9' * (MONEY_DECIMAL_PLACES + 1)
        form = AddFundsForm(data={'money': float(f'1.{dp}')})
        self.assertFalse(form.is_valid())

    def test_negative_money(self):
        """Test case to validate the behavior of 'money' field with negative value."""
        self.assertFalse(AddFundsForm(data={'money': -1}).is_valid())

    def test_zero_money(self):
        """Test case to validate the behavior of 'money' field with zero value."""
        self.assertFalse(AddFundsForm(data={'money': 0}).is_valid())

    def test_valid(self):
        """Test case to validate the behavior of 'money' field with a valid positive amount."""
        self.assertTrue(AddFundsForm(data={'money': 100}).is_valid())


class RegistrationFormTest(TestCase):
    """Test case for the RegistrationForm class."""

    _valid_data = {
        'username': 'username',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email@email.com',
        'password1': 'Azpm1029!',
        'password2': 'Azpm1029!',
    }

    def test_valid(self):
        """Test for validating the registration form with valid data."""
        self.assertTrue(RegistrationForm(data=self._valid_data).is_valid())

    def invalid(self, invalid_data):
        """
        Test for validating the registration form with invalid data.

        Args:
            invalid_data: A tuple containing field-value pairs of invalid data.
        """
        data = self._valid_data.copy()
        for field, value in invalid_data:
            data[field] = value
        self.assertFalse(RegistrationForm(data=data).is_valid())

    def test_short_password(self):
        """Test for validating the registration form with a short password."""
        self.invalid(
            (
                ('password1', 'abc'),
                ('password2', 'abc'),
            ),
        )

    def test_common_password(self):
        """Test for validating the registration form with a common password."""
        self.invalid(
            (
                ('password1', 'abcdef123'),
                ('password2', 'abcdef123'),
            ),
        )

    def test_different_passwords(self):
        """Test for validating the registration form with different passwords."""
        self.invalid(
            (
                ('password1', 'ASDksdjn9734'),
                ('password2', 'LKKJdfnalnd234329'),
            ),
        )

    def test_invalid_email(self):
        """Test for validating the registration form with an invalid email."""
        self.invalid(
            (
                ('email', 'abc'),
            ),
        )

    def test_existing_user(self):
        """Test for validating the registration form with an existing user."""
        username, password = 'username', 'password'
        User.objects.create(username=username, password=password)
        self.invalid(
            (
                ('username', username),
                ('password', password),
            ),
        )
