"""Admin Panel."""
from django.contrib import admin

from .models import Client, Performance, Theater, TheaterPerformance, Ticket


class TheaterPerformanceInline(admin.TabularInline):
    """Inline configuration for TheaterPerformance model."""

    model = TheaterPerformance
    extra = 1


@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    """Admin configuration for Theater model."""

    model = Theater
    inlines = (TheaterPerformanceInline,)


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    """Admin configuration for Performance model."""

    model = Performance
    inlines = (TheaterPerformanceInline,)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin configuration for Ticket model."""

    model = Ticket


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Admin configuration for Client model."""

    model = Client


@admin.register(TheaterPerformance)
class TheaterPerformanceAdmin(admin.ModelAdmin):
    """Admin configuration for TheaterPerformance model."""

    model = TheaterPerformance
