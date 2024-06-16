from django.test import TestCase, client as django_client
from django.contrib.auth.models import User

from theaters_app.models import Client


class TestAddFunds(TestCase):
    _page_url = '/profile/'

    def setUp(self):
        self.user = User.objects.create(username='user', password='user')
        self.client = Client.objects.create(user=self.user, money=0)
        self.api_client = django_client.Client()
        self.api_client.force_login(self.user)

    def test_negative_money(self):
        self.api_client.post(self._page_url, {'money': -1})
        self.client.refresh_from_db()

        self.assertEqual(self.client.money, 0)

    def test_successful(self):
        self.api_client.post(self._page_url, {'money': 1})
        self.client.refresh_from_db()

        self.assertEqual(self.client.money, 1)
