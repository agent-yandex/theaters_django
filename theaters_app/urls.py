"""URL configuration for the theater ticketing web application."""

from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('theaters', views.TheaterViewSet)
router.register('performances', views.PerformanceViewSet)
router.register('tickets', views.TicketViewSet)

urlpatterns = [
    path('', views.main, name='homepage'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('buy/<uuid:ticket_id>', views.buy, name='buy'),

    path('theaters/', views.TheaterListView.as_view(), name='theaters'),
    path('theater/<uuid:theater_id>', views.theater_view, name='theater'),
    path('performances/', views.PerformanceListView.as_view(), name='performances'),
    path('performance/<uuid:performance_id>', views.performance_view, name='performance'),
    path('ticket/<uuid:ticket_id>', views.ticket_view, name='ticket'),

    path('api/', include(router.urls)),
    path('token/', obtain_auth_token),
]
