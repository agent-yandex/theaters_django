"""Module of testing views."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theaters_app.models import Client, Performance, Theater, Ticket


def create_test_with_auth(url, page_name, template, auth=True):
    """
    Create a test method with authentication.

    Args:
        url (str): The URL to test.
        page_name (str): The name of the page.
        template (str): The template to be used.
        auth (bool, optional): Flag to indicate if authentication is required. Defaults to True.

    Returns:
        method: The test method.
    """
    def method(self):
        """
        Test method with authentication.

        Args:
            self: The instance of the test case.
        """
        self.client = APIClient()
        if auth:
            self.user = User.objects.create(username='user', password='user')
            Client.objects.create(user=self.user)
            self.client.force_login(self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTemplateUsed(response, template)

        response = self.client.get(reverse(page_name))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    return method


def create_test_no_auth(url):
    """
    Create a test method without authentication.

    Args:
        url (str): The URL to test.

    Returns:
        method: The test method.
    """
    def method(self):
        """
        Test method without authentication.

        Args:
            self: The instance of the test case.
        """
        self.client = APIClient()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    return method


def create_test_instance(url, model, creation_attrs):
    """
    Create a test method for an instance.

    Args:
        url (str): The URL to test.
        model (class): The model class.
        creation_attrs (dict): Attributes for creating the instance.

    Returns:
        method: The test method.
    """
    def method(self):
        """
        Test method for an instance.

        Args:
            self: The instance of the test case.
        """
        self.client = APIClient()
        self.user = User.objects.create(username='user', password='user')
        Client.objects.create(user=self.user)
        self.target_id = model.objects.create(**creation_attrs).id

        # GET with no auth
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        self.client.force_login(user=self.user)
        # GET WITH auth, but without query
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # GET WITH auth, id in query is invalid
        response = self.client.get(f'{url}?id=123')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # GET with auth and with valid id
        target_url = f'{url}?id={self.target_id}'
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    return method


pages = (
    ('/theaters/', 'theaters', 'catalog/theaters.html'),
    ('/performances/', 'performances', 'catalog/performances.html'),
    ('/profile/', 'profile', 'pages/profile.html'),
)
base_pages = (
    ('', 'homepage', 'index.html'),
    ('/register/', 'register', 'registration/register.html'),
    ('/accounts/login/', 'login', 'registration/login.html'),
)
methods = {
    f'test_{page[1]}': create_test_with_auth(*page) for page in (list(pages) + list(base_pages))
}
TestPagesAuth = type('TestPages', (TestCase,), methods)

methods_no_auth = {f'test_{url}': create_test_no_auth(url) for url, _, _ in pages}
base_pages_no_auth = {
    f'test_{page[1]}': create_test_with_auth(*page, auth=False) for page in base_pages
}
methods_no_auth.update(base_pages_no_auth)
TestPagesNoAuth = type('TestPagesNoAuth', (TestCase,), methods_no_auth)

instances_pages = (
    ('/buy/', Ticket, {'price': 100, 'time': '11:36:59', 'place': '12'}),
    ('/theater/', Theater, {'title': 'Название', 'address': 'Анархии 12', 'rating': 4.01}),
    (
        '/performance/',
        Performance,
        {'title': 'Название', 'description': 'Описание', 'date': '2040-02-23'},
    ),
    ('/ticket/', Ticket),
)
