from datetime import date, datetime, timezone

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from theaters_app import models


def create_test(attr, value):
    def new_test(self):
        data = self._creation_attrs.copy()
        data[attr] = value
        with self.assertRaises(ValidationError):
            self._model_class.objects.create(**data)
    
    return new_test


def create_test_save(attr, value):
    def new_test(self):
        data = self._creation_attrs.copy()
        instance = self._model_class.objects.create(**data)
        setattr(instance, attr, value)
        with self.assertRaises(ValidationError):
            instance.save()

    return new_test


def create_model_test(model_class, creation_attrs, tests):
    class ModelTest(TestCase):
        _model_class = model_class
        _creation_attrs = creation_attrs

        def test_successful_creation(self):
            self._model_class.objects.create(**self._creation_attrs)

    for num, values in enumerate(tests):
        attr, value = values
        setattr(ModelTest, f'test_create_{attr}_{num}', create_test(attr, value))
        setattr(ModelTest, f'test_save_{attr}_{num}', create_test_save(attr, value))

    return ModelTest


theater_attrs = {'title': 'Название', 'address': 'Анархии 12', 'rating': 4.01}
performance_attrs = {'title': 'Название', 'description': 'Описание', 'date': '2040-02-23'}
ticket_attrs = {'price': 100, 'time': '11:36:59', 'place': '12'}

PAST_YEAR = 2007
FUTURE_YEAR = 3000

valid_tests = (
    (models.check_created, datetime(PAST_YEAR, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)),
    (models.check_modified, datetime(PAST_YEAR, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)),
    (models.check_date, date(FUTURE_YEAR, 1, 1)),
    (models.check_positive, 1),
    (models.check_limits, 4),
)
invalid_tests = (
    (models.check_created, datetime(FUTURE_YEAR, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)),
    (models.check_modified, datetime(FUTURE_YEAR, 1, 1, 1, 1, 1, 1, tzinfo=timezone.utc)),
    (models.check_date, date(PAST_YEAR, 1, 1)),
    (models.check_positive, -1),
    (models.check_limits, -1),
)

def create_validation_test(validator, value, valid=True):
    if valid:
        return lambda _: validator(value)
    def test(self):
        with self.assertRaises(ValidationError):
            validator(value)
    return test

valid_methods = {
    f'test_valid_{args[0].__name__}': create_validation_test(*args) for args in valid_tests
}
invalid_methods = {
    f'test_invalid_{args[0].__name__}': create_validation_test(*args, valid=False) for args in invalid_tests
}

TestValidators = type('TestValidators', (TestCase,), valid_methods | invalid_methods)

test_str_data = (
    (models.Theater, theater_attrs, '"Название", Анархии 12, rating - 4.01'),
    (models.Performance, performance_attrs, '"Название", Описание'),
    (models.Ticket, ticket_attrs, 'None, 100р., 11:36:59, 12'),
)


def create_str_test(model, attrs, expected):
    def test(self):
        self.assertEqual(str(model.objects.create(**attrs)), expected)

    return test


test_str_method = {f'test_{args[0].__name__}': create_str_test(*args) for args in test_str_data}
TestStr = type('TestStr', (TestCase,), test_str_method)


class TestLinks(TestCase):
    def test_theater_performance(self):
        theater = models.Theater.objects.create(**theater_attrs)
        performance = models.Performance.objects.create(**performance_attrs)
        theater.performances.add(performance)

        link = models.TheaterPerformance.objects.get(theater=theater, performance=performance)

        self.assertEqual(str(link), f'{theater} - {performance}')

    def test_ticket_theater_performance(self):
        theater = models.Theater.objects.create(**theater_attrs)
        performance = models.Performance.objects.create(**performance_attrs)
        theater.performances.add(performance)
        theater_perfomance = models.TheaterPerformance.objects.get(theater=theater, performance=performance)
        ticket_attrs = {'price': 100, 'time': '11:36:59', 'place': '12', 'theater_performance_id': theater_perfomance.id}
        ticket = models.Ticket.objects.create(**ticket_attrs)

        self.assertEqual(str(ticket.theater_performance), f'{theater} - {performance}')

    def test_ticket_client(self):
        user = User.objects.create(username='test', password='test')
        client = models.Client.objects.create(user=user)
        ticket_attrs = {'price': 100, 'time': '11:36:59', 'place': '12', 'client_id': client.id}
        ticket = models.Ticket.objects.create(**ticket_attrs)

        self.assertEqual(str(client), str(ticket.client))
