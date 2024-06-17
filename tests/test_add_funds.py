"""Unit tests for adding funds functionality in a theater ticketing application."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.test import client as django_client

from theaters_app.models import Client


class TestAddFunds(TestCase):
    """Test case for adding funds to a user's account via the profile page."""

    _page_url = '/profile/'

    def setUp(self):
        """Set up the test environment by creating a User and Client instance."""
        self.user = User.objects.create(username='user', password='user')
        self.client = Client.objects.create(user=self.user, money=0)
        self.api_client = django_client.Client()
        self.api_client.force_login(self.user)

    def test_negative_money(self):
        """Test case to verify that adding a negative amount of money."""
        self.api_client.post(self._page_url, {'money': -1})
        self.client.refresh_from_db()

        self.assertEqual(self.client.money, 0)

    def test_successful(self):
        """Test case to verify successful addition of funds to the Client's balance."""
        self.api_client.post(self._page_url, {'money': 1})
        self.client.refresh_from_db()

        self.assertEqual(self.client.money, 1)
