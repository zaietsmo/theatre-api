from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Actor, Genre, Performance, Play, Reservation, TheatreHall, Ticket


class BaseTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="AdminPass123!"
        )
        self.admin_refresh = RefreshToken.for_user(self.admin_user)
        self.admin_access_token = str(self.admin_refresh.access_token)

        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="UserPass123!"
        )
        self.user_refresh = RefreshToken.for_user(self.user)
        self.user_access_token = str(self.user_refresh.access_token)

        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_row=20
        )

        self.play = Play.objects.create(
            title="Hamlet", description="A tragic play by Shakespeare."
        )

        self.actor = Actor.objects.create(first_name="John", last_name="Doe")
        self.actor.plays.add(self.play)

        self.genre = Genre.objects.create(name="Tragedy")
        self.genre.plays.add(self.play)

        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time=timezone.now() + timedelta(days=1),
        )

        self.play_list_url = reverse("play-list")
        self.actor_list_url = reverse("actor-list")
        self.reservation_list_url = reverse("reservation-list")
        self.performance_list_url = reverse("performance-list")
        self.theatrehall_list_url = reverse("theatrehall-list")


class PlayTests(BaseTestCase):
    def test_create_play(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_access_token}")
        data = {
            "title": "Macbeth",
            "description": "Another tragic play by Shakespeare.",
        }
        response = self.client.post(self.play_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Play.objects.count(), 2)

    def test_get_plays_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_access_token}")
        url = reverse("play-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_plays_as_regular_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}")
        url = reverse("play-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ReservationTests(BaseTestCase):
    def test_create_reservation(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}")
        url = reverse("reservation-list")
        data = {
            "performance_id": self.performance.id,
            "seats": [{"row": 1, "seat": 1}, {"row": 1, "seat": 2}],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 2)

    def test_create_reservation_with_invalid_seats(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}")
        url = reverse("reservation-list")
        data = {
            "performance_id": self.performance.id,
            "seats": [{"row": 100, "seat": 1}, {"row": 1, "seat": 100}],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_reservations(self):
        reservation = Reservation.objects.create(user=self.user)
        Ticket.objects.create(
            row=1, seat=1, performance=self.performance, reservation=reservation
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}")
        response = self.client.get(self.reservation_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class PerformanceTests(BaseTestCase):
    def test_create_performance_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_access_token}")
        url = reverse("performance-list")
        data = {
            "play": self.play.id,
            "theatre_hall": self.theatre_hall.id,
            "show_time": (timezone.now() + timedelta(days=2)).isoformat(),
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_performances_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_access_token}")
        url = reverse("performance-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class TheatreHallTests(BaseTestCase):
    def test_create_theatre_hall_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_access_token}")
        url = reverse("theatrehall-list")
        data = {"name": "Small Hall", "rows": 5, "seats_in_row": 10}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TheatreHall.objects.count(), 2)


class ActorTests(BaseTestCase):
    def test_create_actor_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_access_token}")
        data = {"first_name": "Jane", "last_name": "Smith"}
        response = self.client.post(self.actor_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
