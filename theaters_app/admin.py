from django.contrib import admin

from .models import Theater, Performance, Ticket, Client, TheaterPerformance


class TheaterPerformanceInline(admin.TabularInline):
    model = TheaterPerformance
    extra = 1


# class TicketClientInline(admin.TabularInline):
#     model = Client
#     extra = 1


@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    model = Theater
    inlines = (TheaterPerformanceInline,)


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    model = Performance
    inlines = (TheaterPerformanceInline,)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    model = Ticket


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    model = Client


@admin.register(TheaterPerformance)
class TheaterPerformanceAdmin(admin.ModelAdmin):
    model = TheaterPerformance
