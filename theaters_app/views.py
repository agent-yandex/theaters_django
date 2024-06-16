from typing import Any

from django.shortcuts import render, redirect, get_object_or_404
from django.core import exceptions, paginator as django_paginator
from django.contrib.auth import decorators, mixins
from django.views.generic import ListView
from rest_framework import permissions, viewsets

from .models import Theater, Performance, Ticket, Client, TheaterPerformance
from .serializers import TheaterSerialazer, PerformanceSerialazer, TicketSerialazer
from .forms import RegistrationForm, AddFundsForm


def main(request):
    return render(
        request=request,
        template_name='index.html',
        context={
            'theaters': Theater.objects.count(),
            'performances': Performance.objects.count(),
            'tickets': Ticket.objects.count(),
        }
    )


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Client.objects.create(user=user)
    else:
        form = RegistrationForm()

    return render(
        request=request,
        template_name='registration/register.html',
        context={
            'form': form,
        }
    )


@decorators.login_required
def profile(request):
    client = Client.objects.get(user=request.user)
    tickets = Ticket.objects.filter(client_id=client.id)

    if request.method == 'POST':
        form = AddFundsForm(request.POST)
        if form.is_valid():
            money = form.cleaned_data.get('money', None)
            client.money += money
            client.save()
    else:
        form = AddFundsForm()

    return render(
        request=request,
        template_name='pages/profile.html',
        context={
            'client': client,
            'tickets': tickets,
            'form': form,
        }
    )


def create_list_view(model_class, plural_name, template):
    class CustomListView(mixins.LoginRequiredMixin, ListView):
        model = model_class
        template_name = template
        paginate_by = 10
        context_object_name = plural_name

        def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
            context = super().get_context_data(**kwargs)
            instances = model_class.objects.all()
            paginator = django_paginator.Paginator(instances, 10)
            page = self.request.GET.get('page')
            page_obj = paginator.get_page(page)
            context[f'{plural_name}_list'] = page_obj
            return context

    return CustomListView


TheaterListView = create_list_view(Theater, 'theaters', 'catalog/theaters.html')
PerformanceListView = create_list_view(Performance, 'performances', 'catalog/performances.html')
TicketListView = create_list_view(Ticket, 'tickets', 'catalog/tickets.html')


@decorators.login_required
def theater_view(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    context = {
        'theater': theater,
    }

    return render(request=request, template_name='entities/theater.html', context=context)


@decorators.login_required
def performance_view(request, performance_id):
    performance = get_object_or_404(Performance, id=performance_id)
    theater_performances = TheaterPerformance.objects.filter(performance_id=performance)

    free_tickets = []
    for t_p in theater_performances:
        tickets = Ticket.objects.filter(theater_performance_id=t_p.id)
        free_tickets += [ticket for ticket in tickets if not ticket.client]

    context = {
        'performance': performance,
        'tickets': free_tickets,
    }

    return render(request=request, template_name='entities/performance.html', context=context)


@decorators.login_required
def ticket_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    client = Client.objects.get(user=request.user)
    if ticket.theater_performance_id:
        theater_performance = TheaterPerformance.objects.get(id=ticket.theater_performance_id)
    else:
        theater_performance = None

    context = {
        'ticket': ticket,
        'client': client,
        'theater_performance': theater_performance,
    }

    return render(request=request, template_name='entities/ticket.html', context=context)


@decorators.login_required
def buy(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    client = Client.objects.get(user=request.user)
    if request.method == 'POST' and client.money >= ticket.price:
        ticket.client_id = client.id
        client.money -= ticket.price
        ticket.save()
        client.save()
        return redirect('profile')
    
    return render(
        request=request,
        template_name='pages/buy.html',
        context={
            'ticket': ticket,
            'client': client,
            'test': client.id == ticket.client_id,
        }
    )



class APIPermission(permissions.BasePermission):
    _allowed_methods = ['GET', 'OPTIONS', 'HEAD']
    _not_allowed_methods = ['POST', 'PUT', 'DELETE']

    def has_permission(self, request, view):
        if request.method in self._allowed_methods and (request.user.is_authenticated and request.user.is_authenticated):
            return True
        if request.method in self._not_allowed_methods and (request.user and request.user.is_superuser):
            return True

        return False


def create_view_set(model_class, serializer):
    class CustomViewSet(viewsets.ModelViewSet):
        queryset = model_class.objects.all()
        serializer_class = serializer
        permission_classes = [APIPermission]

    return CustomViewSet


TheaterViewSet = create_view_set(Theater, TheaterSerialazer)
PerformanceViewSet = create_view_set(Performance, PerformanceSerialazer)
TicketViewSet = create_view_set(Ticket, TicketSerialazer)
