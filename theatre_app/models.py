from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, username=None, password=None,*args,**kwargs):
        if not username:
            raise ValueError("Users must have a username")
        if not password:
            raise ValueError("Users must have a password")
        user= self.model(
            username=username,
            *args,
            **kwargs)
        user.set_password(password)
        user.is_active=True
        user.save()
        return user

    def create_superuser(self, username, password,email):
        user = self.create_user(
            username=username,
            password=password,
            email=email,
            role=1, 
            is_staff=True,
        )
        user.is_superuser = True
        user.save()
        return user

ROLE_CHOICES = (
        ('1', 'Admin'),
        ('2', 'Theatre Operator'),
        ('3', 'User'),
    )

class CustomUser(AbstractBaseUser,PermissionsMixin):

    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    role = models.IntegerField(choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def _str_(self):
        return self.username
    
    


from django.db import models
from .models import CustomUser

class Theatre_Profile(models.Model):
   
    fk_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  
    location = models.CharField(max_length=255, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    def _str_(self):
        return f"{self.user.username} ({self.role})"





class Movie(models.Model):
    fk_theatre = models.ForeignKey(Theatre_Profile, on_delete=models.CASCADE, related_name='movies')
    movie_name = models.CharField(max_length=255)
    movie_description = models.TextField()
    movie_genre = models.CharField(max_length=100)
    movie_language = models.CharField(max_length=100)
    movie_cast = models.TextField()
    movie_crew = models.TextField()
    movie_screen = models.CharField(max_length=100)  # e.g., "Screen 1", "Screen 2"
    movie_trailer = models.FileField(upload_to='trailers/', blank=True, null=True)
    movie_image = models.ImageField(upload_to='movies/', blank=True, null=True)
    movie_certificate = models.CharField(max_length=10)  # E.g., "U", "A", "PG"
    movie_duration = models.PositiveIntegerField()  # Duration in minutes
    movie_release_date = models.DateField()
    movie_is_3d = models.BooleanField(default=False)  # True if movie is 3D, False if 2D
    
    def _str_(self):
        return self.movie_name
    


from django.db import models

from django.db import models

class ShowTime(models.Model):
    fk_movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    show_time = models.TimeField(max_length=10)  # Example: "10:00 AM", "7:00 PM"

    def __str__(self):
        return f"{self.fk_movie.movie_name} - {self.show_time}"

class ShowtimeDate(models.Model):
    showtime = models.ForeignKey(ShowTime, on_delete=models.CASCADE, related_name="dates")
    date = models.DateField()

    def __str__(self):
        return f"{self.showtime.fk_movie.movie_name} - {self.date}"


class Seat(models.Model):
    fk_showtime = models.ForeignKey(ShowTime, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.CharField(max_length=10)  # Example: XA1, XA2, etc.
    is_booked = models.BooleanField(default=False)
    row = models.CharField(max_length=5, default="A")
    booked_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.seat_number} - {'Booked' if self.is_booked else 'Available'}"


class Booking(models.Model):
    CANCELLATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('none', 'None')  # Default state when not canceled
    ]
    fk_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    fk_seat = models.OneToOneField(Seat, on_delete=models.CASCADE, related_name='booking')
    booking_type = models.CharField(max_length=10, choices=[('direct', 'Direct Booking'), ('flexi', 'Flexi Booking')])
    payment_method = models.CharField(max_length=10, choices=[('gpay', 'Google Pay'), ('phonepe', 'PhonePe'), ('paytm', 'Paytm')])
    booking_date = models.DateTimeField()
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True, null=True)
    cancellation_status = models.CharField(max_length=10, choices=CANCELLATION_STATUS_CHOICES, default='none')

    def __str__(self):
        return f"{self.fk_user.username} booked {self.fk_seat.seat_number}"
    



    #################################################

class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(default=0)  # Rating out of 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} rated {self.movie.movie_name} {self.rating}/5"
    

####################################################################################################

class Complaint(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"Complaint by {self.user.username}"
    

#####################################################################################

class TheatreComplaint(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre_Profile, on_delete=models.CASCADE)
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint by {self.user.username} to {self.theatre.fk_user.username}"
    

###########################################################################

class Theatre_Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre_Profile, on_delete=models.CASCADE, related_name='tratings')
    rating = models.IntegerField(default=0)  # Rating out of 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} rated {self.theatre.name} {self.rating}/5"
