from django.core.exceptions import ValidationError
from django.db import models


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self):
        return self.name


class Performance(models.Model):
    play = models.ForeignKey(Play, on_delete=models.CASCADE)
    theatre_hall = models.ForeignKey(TheatreHall, on_delete=models.CASCADE)
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["show_time"]

    def __str__(self):
        return f"{self.play.title} at {self.show_time}"


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    plays = models.ManyToManyField(Play, related_name="actors")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=255)
    plays = models.ManyToManyField(Play, related_name="genres")

    def __str__(self):
        return self.name


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    performance = models.ForeignKey(
        Performance, on_delete=models.CASCADE, related_name="reservations"
    )

    def __str__(self):
        return f"Reservation by {self.user.username} for {self.performance}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(
        Performance, on_delete=models.CASCADE, related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name="tickets"
    )
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ["performance", "row", "seat"]

    def __str__(self):
        return f"Row {self.row} Seat {self.seat} - {self.performance}"

    def clean(self):
        if (
            Ticket.objects.filter(
                performance=self.performance, row=self.row, seat=self.seat
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("This seat is already booked.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
