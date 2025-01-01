from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import Actor, Genre, Performance, Play, Reservation, TheatreHall, Ticket


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class PlaySerializer(serializers.ModelSerializer):
    actors = serializers.StringRelatedField(many=True, required=False)
    genres = serializers.StringRelatedField(many=True, required=False)

    class Meta:
        model = Play
        fields = ["id", "title", "description", "actors", "genres"]


class PerformanceSerializer(serializers.ModelSerializer):
    play = serializers.PrimaryKeyRelatedField(queryset=Play.objects.all())
    theatre_hall = serializers.PrimaryKeyRelatedField(
        queryset=TheatreHall.objects.all()
    )

    def validate_show_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Show time cannot be in the past")
        return value

    class Meta:
        model = Performance
        fields = ["id", "play", "theatre_hall", "show_time"]


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ["id", "name", "rows", "seats_in_row"]


class ActorSerializer(serializers.ModelSerializer):
    plays = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Play.objects.all(), required=False
    )

    class Meta:
        model = Actor
        fields = ["id", "first_name", "last_name", "plays"]


class GenreSerializer(serializers.ModelSerializer):
    plays = serializers.StringRelatedField(many=True)

    class Meta:
        model = Genre
        fields = ["id", "name", "plays"]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "performance", "reservation"]
        read_only_fields = ["performance", "reservation"]


class ReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    performance_id = serializers.IntegerField(write_only=True)
    seats = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()), write_only=True
    )
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = ["id", "created_at", "user", "performance_id", "seats", "tickets"]

    def validate(self, attrs):
        performance_id = attrs.get("performance_id")
        seats = attrs.get("seats")

        try:
            performance = Performance.objects.get(id=performance_id)
        except Performance.DoesNotExist:
            raise serializers.ValidationError(
                {"performance_id": "Performance does not exist."}
            )

        for seat in seats:
            row = seat.get("row")
            number = seat.get("seat")
            if not (1 <= row <= performance.theatre_hall.rows):
                raise serializers.ValidationError(
                    {"seats": f"Row {row} is out of bounds."}
                )
            if not (1 <= number <= performance.theatre_hall.seats_in_row):
                raise serializers.ValidationError(
                    {"seats": f"Seat {number} in row {row} is out of bounds."}
                )
            if Ticket.objects.filter(
                performance=performance, row=row, seat=number
            ).exists():
                raise serializers.ValidationError(
                    {"seats": f"Seat {number} in row {row} is already reserved."}
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        performance_id = validated_data.pop("performance_id")
        seats = validated_data.pop("seats")

        performance = Performance.objects.get(id=performance_id)

        reservation = Reservation.objects.create(user=user)

        tickets = []
        for seat in seats:
            ticket = Ticket.objects.create(
                performance=performance,
                reservation=reservation,
                row=seat["row"],
                seat=seat["seat"],
            )
            tickets.append(ticket)

        return reservation
