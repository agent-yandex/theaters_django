from rest_framework import serializers

from .models import Theater, Performance, Ticket


class TheaterSerialazer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Theater
        fields = '__all__'


class PerformanceSerialazer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Performance
        fields = '__all__'


class TicketSerialazer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
