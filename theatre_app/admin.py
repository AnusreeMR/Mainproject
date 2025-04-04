from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    Theatre_Profile,
    ROLE_CHOICES,
    Movie
)

class CustomUserAdmin(UserAdmin):
    # Fields to display in the admin user list view
    list_display = ('username', 'email', 'get_role_with_id', 'is_staff', 'is_active')
    
    # Fields to enable filtering by
    list_filter = ('role', 'is_staff', 'is_active')
    
    # Fields to enable search on
    search_fields = ('username', 'email')
    
    # Fieldsets for the detail view
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    # Fields for the 'Add User' form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )
    
    # Default ordering in the admin list view
    ordering = ('email',)

    # Custom method to display role with ID
    def get_role_with_id(self, obj):
        role_dict = dict(ROLE_CHOICES)  # Convert choices to a dictionary for easy lookup
        return f"{obj.role} ({role_dict.get(str(obj.role), 'Unknown')})"
    get_role_with_id.short_description = 'Role'

admin.site.register(CustomUser, CustomUserAdmin)

# Admin classes for profile models
@admin.register(Theatre_Profile)
class TheatreProfileAdmin(admin.ModelAdmin):
    list_display = ('fk_user', 'location', 'mobile_number')



admin.site.register(Movie)

from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'fk_user', 'fk_seat', 'booking_type', 'payment_method', 'booking_date', 'is_cancelled')
    list_filter = ('booking_type', 'payment_method', 'is_cancelled', 'booking_date')
    search_fields = ('fk_user__username', 'fk_seat__seat_number')
    ordering = ('-booking_date',)


from django.contrib import admin
from .models import Movie, ShowTime, ShowtimeDate

@admin.register(ShowTime)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ("fk_movie", "show_time")  # Display movie name and show time
    list_filter = ("fk_movie",)  # Add a filter by movie
    search_fields = ("fk_movie__movie_name", "show_time")  # Enable search by movie name and time

@admin.register(ShowtimeDate)
class ShowtimeDateAdmin(admin.ModelAdmin):
    list_display = ("showtime", "date")  # Display showtime and date
    list_filter = ("date", "showtime__fk_movie")  # Filter by date and movie
    search_fields = ("showtime__fk_movie__movie_name", "date")  # Search by movie name and date


###########################################
from django.contrib import admin
from .models import Complaint, TheatreComplaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'reply_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'message')

    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Message"

    def reply_preview(self, obj):
        return obj.reply[:50] + "..." if obj.reply and len(obj.reply) > 50 else obj.reply
    reply_preview.short_description = "Reply"

@admin.register(TheatreComplaint)
class TheatreComplaintAdmin(admin.ModelAdmin):
    list_display = ('user', 'theatre', 'message_preview', 'reply_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'theatre')
    search_fields = ('user__username', 'theatre__fk_user__username', 'message')

    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Message"

    def reply_preview(self, obj):
        return obj.reply[:50] + "..." if obj.reply and len(obj.reply) > 50 else obj.reply
    reply_preview.short_description = "Reply"
