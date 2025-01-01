from django.contrib.auth.models import User
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Actor, Genre, Performance, Play, Reservation, TheatreHall, Ticket
from .serializers import (
    ActorSerializer,
    GenreSerializer,
    PerformanceSerializer,
    PlaySerializer,
    ReservationSerializer,
    TheatreHallSerializer,
    TicketSerializer,
    UserSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema_view(
    list=extend_schema(
        summary="List all plays",
        description="Retrieve a list of all plays. Admins only.",
    ),
    create=extend_schema(
        summary="Create a new play", description="Admins can create a new play."
    ),
)
class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


@extend_schema_view(
    list=extend_schema(
        summary="List all actors",
        description="Retrieve a list of all actors. Admins only.",
    ),
    create=extend_schema(
        summary="Create a new actor", description="Admins can create a new actor."
    ),
)
class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


@extend_schema_view(
    list=extend_schema(
        summary="List all genres",
        description="Retrieve a list of all genres. Admins only.",
    ),
    create=extend_schema(
        summary="Create a new genre", description="Admins can create a new genre."
    ),
)
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


@extend_schema_view(
    list=extend_schema(
        summary="List all theatre halls",
        description="Retrieve a list of all theatre halls. Admins only.",
    ),
    create=extend_schema(
        summary="Create a new theatre hall",
        description="Admins can create a new theatre hall.",
    ),
)
class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


@extend_schema_view(
    list=extend_schema(
        summary="List all performances",
        description="Retrieve a list of all performances. Admins only.",
    ),
    create=extend_schema(
        summary="Create a new performance",
        description="Admins can create a new performance.",
    ),
)
class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["play", "theatre_hall", "show_time"]
    search_fields = ["play__title"]
    ordering_fields = ["show_time", "play__title"]


@extend_schema_view(
    list=extend_schema(
        summary="List all reservations",
        description="Admins can view all reservations. Users can view their own.",
    ),
    create=extend_schema(
        summary="Create a new reservation",
        description="Authenticated users can create a reservation.",
    ),
)
class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Reservation.objects.all()
        return Reservation.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.context["request"] = request
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


@extend_schema_view(
    list=extend_schema(
        summary="List all tickets",
        description="Retrieve a list of all tickets. Authenticated users only.",
    ),
    create=extend_schema(
        summary="Create a new ticket",
        description="Authenticated users can create a new ticket.",
    ),
)
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(
        summary="List all users", description="Admins can view all users."
    ),
    retrieve=extend_schema(
        summary="Retrieve a specific user",
        description="Admins can retrieve user details by ID.",
    ),
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
