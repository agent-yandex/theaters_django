"""Module with serializers for different models."""

from rest_framework import serializers

from .models import Performance, Theater, Ticket


class TheaterSerialazer(serializers.HyperlinkedModelSerializer):
    """Serializer for the Theater model."""

    class Meta:
        """Meta class."""

        model = Theater
        fields = '__all__'


class PerformanceSerialazer(serializers.HyperlinkedModelSerializer):
    """Serializer for the Performance model."""

    class Meta:
        """Meta class."""

        model = Performance
        fields = '__all__'


class TicketSerialazer(serializers.HyperlinkedModelSerializer):
    """Serializer for the Ticket model."""

    class Meta:
        """Meta class."""

        model = Ticket
        fields = '__all__'
