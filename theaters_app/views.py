"""Contains views for rendering HTML templates and processing user requests."""

from typing import Any

from django.contrib.auth import decorators, mixins
from django.core import paginator as django_paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from rest_framework import permissions, viewsets

from .forms import AddFundsForm, RegistrationForm
from .models import Client, Performance, Theater, TheaterPerformance, Ticket
from .serializers import PerformanceSerialazer, TheaterSerialazer, TicketSerialazer


def main(request):
    """
    View function for rendering the homepage.

    Args:
        request: Request object.

    Returns:
        HttpResponse: Rendered HTML template.
    """
    return render(
        request=request,
        template_name='index.html',
        context={
            'theaters': Theater.objects.count(),
            'performances': Performance.objects.count(),
            'tickets': Ticket.objects.count(),
        },
    )


def register(request):
    """
    View function for rendering the registration page and processing registration requests.

    Args:
        request: Request object.

    Returns:
        HttpResponse: Rendered HTML template.
    """
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
        },
    )


@decorators.login_required
def profile(request):
    """
    View function for rendering the user profile page.

    Args:
        request: Request object.

    Returns:
        HttpResponse: Rendered HTML template.
    """
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
        },
    )


def create_list_view(model_class, plural_name, template):
    """
    Create a ListView with pagination for a given model class.

    Args:
        model_class (type): class of the model
        plural_name (str): plural name of view to name listview
        template (str): path to template for listview

    Returns:
        type: class, which is created dynamic
    """
    class CustomListView(mixins.LoginRequiredMixin, ListView):
        """Class, which is created dynamic, for view list of some model."""

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
    """
    View function for rendering the company detail page.

    Args:
        request: Request object.
        theater_id (int): Theater ID.

    Returns:
        HttpResponse: Rendered HTML template.
    """
    theater = get_object_or_404(Theater, id=theater_id)
    context = {
        'theater': theater,
    }

    return render(request=request, template_name='entities/theater.html', context=context)


@decorators.login_required
def performance_view(request, performance_id):
    """
    View function for rendering the company detail page.

    Args:
        request: Request object.
        performance_id (int): Performance ID.

    Returns:
        HttpResponse: Rendered HTML template.
    """
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
    """
    View function for rendering the company detail page.

    Args:
        request: Request object.
        ticket_id (int): Ticket ID.

    Returns:
        HttpResponse: Rendered HTML template.
    """
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
    """
    Handle the ticket purchase process for authenticated users.

    Args:
        request (HttpRequest): The HTTP request object.
        ticket_id (int): The ID of the ticket to be purchased.

    Returns:
        HttpResponse: Rendered HTML template.
    """
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
        },
    )


class APIPermission(permissions.BasePermission):
    """Permission class for API views to control access."""

    _allowed_methods = ['GET', 'OPTIONS', 'HEAD']
    _not_allowed_methods = ['POST', 'PUT', 'DELETE']

    def has_permission(self, request, _):
        """
        Check if the requesting user has permission to access the view based on the request method.

        Args:
            request (HttpRequest): The incoming request object.
            _: Unused parameter.

        Returns:
            bool: True if the user has permission. False otherwise.
        """
        if request.user and request.user.is_authenticated:
            if request.method in self._allowed_methods:
                return True
            if request.method in self._not_allowed_methods and request.user.is_superuser:
                return True
        return False


def create_view_set(model_class, serializer):
    """
    Create a custom ViewSet class for the given model and serializer.

    Args:
        model_class (type): The model class for which the ViewSet is being created.
        serializer (type): The serializer class to be used with the ViewSet.

    Returns:
        CustomViewSet: A custom ViewSet class that extends viewsets.ModelViewSet.
    """
    class CustomViewSet(viewsets.ModelViewSet):
        """Custom ViewSet class for handling CRUD operations on the provided model."""

        queryset = model_class.objects.all()
        serializer_class = serializer
        permission_classes = [APIPermission]

    return CustomViewSet


TheaterViewSet = create_view_set(Theater, TheaterSerialazer)
PerformanceViewSet = create_view_set(Performance, PerformanceSerialazer)
TicketViewSet = create_view_set(Ticket, TicketSerialazer)
