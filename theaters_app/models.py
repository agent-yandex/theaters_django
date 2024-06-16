from uuid import uuid4

from django.db import models
from datetime import datetime, timezone, date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf.global_settings import AUTH_USER_MODEL


def get_datetime() -> datetime:
    return datetime.now(timezone.utc)


def check_created(dt: datetime) -> None:
    if dt > get_datetime():
        raise ValidationError(
            _('Date and time is bigger than current!'),
            params={'modified': dt},
        )


def check_modified(dt: datetime) -> None:
    if dt > get_datetime():
        raise ValidationError(
            _('Date and time is bigger than current!'),
            params={'modified': dt},
        )


def check_positive(number: float | int) -> None:
    if number < 0:
        raise ValidationError(
            _('Value has to be greater than zero'),
        )


def check_limits(number: float | int) -> None:
    if number < 0 or number > 5:
        raise ValidationError(
            _('Value has to be greater than zero and less than five'),
        )


def check_date(date: date) -> None:
    if date < get_datetime().date():
        raise ValidationError(
            _('Date is less than current!'),
        )


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class CreatedMixin(models.Model):
    created = models.DateTimeField(
        _('created'), null=True, blank=True,
        default=get_datetime, validators=[check_created],
    )

    class Meta:
        abstract = True


class ModifiedMixin(models.Model):
    modified = models.DateTimeField(
        _('modified'), null=True, blank=True,
        default=get_datetime, validators=[check_modified],
    )

    class Meta:
        abstract = True


class Theater(UUIDMixin, CreatedMixin, ModifiedMixin):
    title = models.TextField(_('title'), null=False, blank=False)
    address = models.TextField(_('address'), null=False, blank=False)
    rating = models.DecimalField(
        verbose_name=_('rating'),
        default=5,
        validators=[check_limits],
        decimal_places=2,
        max_digits=3
    )

    performances = models.ManyToManyField(
        to='Performance',
        verbose_name=_('performances'),
        through='TheaterPerformance',
    )

    def __str__(self) -> str:
        return f'"{self.title}", {self.address}, rating - {self.rating}'
    
    class Meta:
        db_table = '"api_data"."theater"'
        ordering = ['rating', 'title', 'address']
        verbose_name = _('theater')
        verbose_name_plural = _('theaters')


class Performance(UUIDMixin, CreatedMixin, ModifiedMixin):
    title = models.TextField(_('title'), null=False, blank=False)
    description = models.TextField(_('description'), null=False, blank=False)
    date = models.DateField(_('date'), null=False, blank=False, validators=[check_date])

    theaters = models.ManyToManyField(
        to='Theater',
        verbose_name=_('theaters'),
        through='TheaterPerformance',
    )

    def __str__(self) -> str:
        return f'"{self.title}", {self.description}'
    
    class Meta:
        db_table = '"api_data"."performance"'
        ordering = ['title']
        verbose_name = _('performance')
        verbose_name_plural = _('performances')


class TheaterPerformance(UUIDMixin, CreatedMixin):
    theater = models.ForeignKey(Theater, verbose_name=_('theater'), on_delete=models.CASCADE)
    performance = models.ForeignKey(Performance, verbose_name=_('performance'), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.theater} - {self.performance}'
    
    class Meta:
        db_table = '"api_data"."theater_performance"'
        unique_together = (
            ('theater', 'performance'),
        )
        verbose_name = _('relationship theater performance')
        verbose_name_plural = _('relationships theater performance')


class Client(UUIDMixin, CreatedMixin, ModifiedMixin):
    money = models.DecimalField(
        verbose_name=_('money'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[check_positive],
    )
    user = models.OneToOneField(
        AUTH_USER_MODEL,
        verbose_name=_('user'),
        null=False,
        blank=False, 
        unique=True,
        on_delete=models.CASCADE,
    )

    @property
    def username(self) -> str:
        return self.user.username
    
    @property
    def first_name(self) -> str:
        return self.user.first_name
    
    @property
    def last_name(self) -> str:
        return self.user.last_name
    
    @property
    def email(self) -> str:
        return self.user.email
    
    def __str__(self) -> str:
        return f'{self.username} {self.first_name} {self.last_name}'

    class Meta:
        db_table = '"api_data"."client"'
        verbose_name = _('client')
        verbose_name_plural = _('clients')


class Ticket(UUIDMixin, CreatedMixin, ModifiedMixin):
    price = models.DecimalField(
        verbose_name=_('price'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[check_positive],
    )
    time = models.TimeField(_('time'), null=False, blank=False)
    place = models.TextField(_('place'), null=False, blank=False)

    theater_performance = models.ForeignKey(
        to=TheaterPerformance,
        verbose_name=_('theater_performance'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    client = models.ForeignKey(
        to=Client,
        verbose_name=_('client'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f'{self.theater_performance}, {self.price}р., {self.time}, {self.place}'

    class Meta:
        db_table = '"api_data"."ticket"'
        ordering = ['place']
        verbose_name = _('ticket')
        verbose_name_plural = _('tickets')


# class TicketClient(UUIDMixin, CreatedMixin):
#     ticket = models.ForeignKey(Ticket, verbose_name=_('ticket'), on_delete=models.CASCADE)
#     client = models.ForeignKey(Client, verbose_name=_('client'), on_delete=models.CASCADE)

#     class Meta:
#         db_table = '"api_data"."ticket_client"'
#         verbose_name = _('relationship ticket client')
#         verbose_name_plural = _('relationships ticket client')
#         unique_together = (
#             ('ticket', 'client'),
#         )
