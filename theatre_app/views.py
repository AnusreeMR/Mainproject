from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from datetime import datetime


# Create your views here.


def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = 3  # Doctor

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('user_register') 
        
        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )
        messages.success(request, "Registration successful! Please log in.")
        return redirect('user_login')
    
    return render(request, 'user/user_register.html')



def theatre_operator_register(request):
    if request.method == 'POST':
        name = request.POST.get('theatre_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        location = request.POST.get('location')
        mobile_number = request.POST.get('mobile_number')
        role = 2

        # Validate Password and Confirm Password
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('theatre_operator_register')

        try:
            # Create User
            user = CustomUser.objects.create_user(
                
                username=name,
                email=email, 
                password=password,
                role=role
                
                )
            
            # Assign Role and Additional Details
            Theatre_Profile.objects.create(
                fk_user=user,
                location=location,
                mobile_number=mobile_number,
            )

            messages.success(request, "Theatre Operator registered successfully!")
            return redirect('user_login')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('theatre_operator_register')

    return render(request, 'theatre/theatre_operator_register.html')



from django.contrib.auth.decorators import login_required


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print(user)  # Print the user object for debugging
            print(type(user))  # Print the type to ensure it's a CustomUser
            
            login(request, user)

            if user.role == 1:  # Admin
                return redirect('admin_dashboard')
            elif user.role == 2:  # Doctor
                return redirect('theatre_operator_dashboard')
            elif user.role == 3:  # Pharmacist
                return redirect('user_dashboard')
            else:
                # Redirect if role is undefined
                return redirect('unknown_role_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('user_login')  # Redirect back to login page

    return render(request, 'register/user_login.html')



def user_list1(request):
    cus_users=CustomUser.objects.filter(role=3)
    return render(request,'admin/user_list1.html',{'cus_users':cus_users})



def theatre_list(request):
    cus_users=CustomUser.objects.filter(role=2)
    return render(request,'admin/theatre_list.html',{'cus_users':cus_users})

def user_delete(req, id):
    user = CustomUser.objects.get(id=id)
    if user:
        user.delete()
    return redirect("user_list1")

def user_layout(request): # Get all theatre profiles
    return render(request, 'user/user_layout.html')

def user_dashboard(request):
    movies_list=Movie.objects.all()
    return render(request,'user/user_dashboard.html',{'movies_list':movies_list})

def admin_dashboard(request):
    return render(request,'admin/admin_dashboard.html')

def theatre_operator_dashboard(request):
    theatre = Theatre_Profile.objects.filter(fk_user=request.user)
    return render(request,'theatre/theatre_operator_dashboard.html',{'theatre':theatre})


def user_logout(request):
    logout(request)  # Logs out the user and clears the session
    return redirect('user_login')  # Redirect to the login page or homepage




# Forgot and Reste Password 

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(f"/reset_password/{uid}/{token}/")

            # Send reset email
            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_url}",
                from_email=None,  # Use DEFAULT_FROM_EMAIL
                recipient_list=[email],
            )

            messages.success(request, "A password reset link has been sent to your email.")
            return render(request, 'register/forgot_password.html', {'success_message': "A password reset link has been sent to your email."})
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
            return render(request, 'register/forgot_password.html', {'error_message': "No account found with that email."})

    return render(request, 'register/forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password has been reset successfully.")
                return redirect('user_login')
            else:
                messages.error(request, "Passwords do not match.")
                return redirect(request.path)

        return render(request, 'register/reset_password.html')
    else:
        messages.error(request, "Invalid or expired token.")
        return redirect('forgot_password')




def the_gg(request):
    return render(request,'user/user_layout.html')

from django.shortcuts import render, redirect
from .models import Movie

def theatre_add_movies(request):
    if request.method == "POST":
        movie_name = request.POST.get("movie_name")
        movie_genre = request.POST.get("movie_genre")
        movie_language = request.POST.get("movie_language")
        movie_duration = request.POST.get("movie_duration")
        movie_cast = request.POST.get("movie_cast")
        movie_crew = request.POST.get("movie_crew")
        movie_release_date = request.POST.get("movie_release_date")
        movie_certificate = request.POST.get("movie_certificate")
        # movie_time_slot = request.POST.get("movie_time_slot")
        movie_screen = request.POST.get("movie_screen")
        movie_description = request.POST.get("movie_description")
        movie_is_3d = request.POST.get("movie_is_3d") == "on"
        movie_image = request.FILES.get("movie_image")  # Ensure it's in request.FILES
        movie_trailer = request.FILES.get("movie_trailer")  # Ensure it's in request.FILES

        # Create a new Movie object with the provided data
        movie = Movie(
            fk_theatre=request.user.theatre_profile,  # Assuming this is correct based on your setup
            movie_name=movie_name,
            movie_genre=movie_genre,
            movie_language=movie_language,
            movie_duration=movie_duration,
            movie_cast = movie_cast,
            movie_crew = movie_crew,
            movie_release_date=movie_release_date,
            movie_certificate = movie_certificate,
            # movie_time_slot=movie_time_slot,
            movie_screen=movie_screen,
            movie_description=movie_description,
            movie_is_3d=movie_is_3d,
            movie_image=movie_image,
            movie_trailer=movie_trailer,  # Save the video file
        )

        # Save the movie instance
        movie.save()

        return redirect("theatre_show_movies")  # Redirect after saving

    return render(request, "theatre/add_movies.html")


from django.shortcuts import render
from .models import Theatre_Profile, Movie

def theatre_show_movies(request):
    user = request.user

    # Get the theatre profile for the logged-in user
    try:
        theatre_profile = Theatre_Profile.objects.get(fk_user=user)

        # Fetch movies associated with this theatre
        movies = Movie.objects.filter(fk_theatre=theatre_profile)
    except Theatre_Profile.DoesNotExist:
        # Handle the case where the user has no associated Theatre_Profile
        movies = []

    return render(request, 'theatre/movies_list.html', {"movies": movies})




# views.py

from django.shortcuts import render, redirect
from .models import Movie

def theatre_edit_movies(request, id):
    
    movie = Movie.objects.get(id=id)

    if request.method == "POST":
        # Retrieve form data
        movie_name = request.POST.get("movie_name")
        movie_genre = request.POST.get("movie_genre")
        movie_language = request.POST.get("movie_language")
        movie_duration = request.POST.get("movie_duration")
        movie_cast = request.POST.get("movie_cast")
        movie_crew = request.POST.get("movie_crew")
        movie_release_date = request.POST.get("movie_release_date")
        movie_certificate = request.POST.get("movie_certificate")

        # movie_time_slot = request.POST.get("movie_time_slot")
        movie_screen = request.POST.get("movie_screen")
        movie_description = request.POST.get("movie_description")
        movie_is_3d = request.POST.get("movie_is_3d") == "on"
        movie_image = request.FILES.get("movie_image")
        movie_trailer = request.FILES.get("movie_trailer") 
        
        if movie_name:
            movie.movie_name = movie_name
        if movie_cast:
            movie.movie_cast = movie_cast
        if movie_crew:
            movie.movie_crew = movie_crew
        if movie_genre:
            movie.movie_genre = movie_genre
        if movie_language:
            movie.movie_language = movie_language
        if movie_duration:
            movie.movie_duration = movie_duration
        if movie_release_date:
            movie.movie_release_date = movie_release_date
        if movie_certificate:
            movie.movie_certificate = movie_certificate

        # if movie_time_slot:
        #     movie.movie_time_slot = movie_time_slot
        if movie_screen:
            movie.movie_screen = movie_screen
        if movie_description:
            movie.movie_description = movie_description
        if movie_is_3d is not None:
            movie.movie_is_3d = movie_is_3d

        # If a new image is provided, update it
        if movie_image:
            movie.movie_image = movie_image

        # If a new trailer is provided, update it
        if movie_trailer:
            movie.movie_trailer = movie_trailer

        # Save the updated movie object
        movie.save()

        # Redirect to the movie list page
        return redirect("theatre_show_movies")

    # If GET request, pre-populate the form with existing movie details
    return render(request, "theatre/edit_movies.html", {"movie": movie})



def theatre_delete_movies(request, id):
    # Get the movie object using the movie id
    movie = Movie.objects.get(id=id)

    # Check if the current user is authorized to delete the movie
    if movie.fk_theatre == request.user.theatre_profile:  # Ensure the movie belongs to the current theatre profile
        # Delete the movie from the database
        movie.delete()

    # Redirect to the movie list page after deletion
    return redirect('theatre_show_movies')


def landing(req):
    movies = Movie.objects.order_by('-id')[:8]  # Fetch latest 5 movies
    return render(req, 'admin/landing.html', {'movies': movies})


def theatre_movies(request, theatre_id):
    movies = Movie.objects.filter(fk_theatre_id=theatre_id)
    theatre = CustomUser.objects.get(id=theatre_id)

    # Create a list of movies with their respective showtimes
    movies_with_showtimes = []
    for movie in movies:
        showtimes = ShowTime.objects.filter(fk_movie=movie)  # Get full ShowTime objects
        movies_with_showtimes.append({'movie': movie, 'showtimes': showtimes})

    return render(request, 'user/theatre_movies.html', {
        'theatre': theatre,
        'movies_with_showtimes': movies_with_showtimes
    })


from django.shortcuts import render, get_object_or_404, redirect
from .models import ShowTime, Movie, Theatre_Profile

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import ShowTime, Movie, Theatre_Profile

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Theatre_Profile, Movie, ShowTime, ShowtimeDate
from django.views.decorators.http import require_POST

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Theatre_Profile, Movie, ShowTime, ShowtimeDate

def theatre_shows(request):
    if not request.user.is_authenticated or request.user.role != 2:  # Role 2 = Theatre Operator
        return redirect('home')

    try:
        theatre = Theatre_Profile.objects.get(fk_user=request.user)
        movies = Movie.objects.filter(fk_theatre=theatre)
        showtimes = ShowTime.objects.filter(fk_movie__fk_theatre=theatre)
    except Theatre_Profile.DoesNotExist:
        movies = []
        showtimes = []

    if request.method == "POST":
        action = request.POST.get('action')

        # CREATE or UPDATE showtime
        if action in ["create", "update"]:
            movie_id = request.POST.get('fk_movie')
            show_time = request.POST.get('show_time')
            new_dates = set(request.POST.getlist('showtime_dates[]'))
            
            movie = get_object_or_404(Movie, id=movie_id, fk_theatre=theatre)

            if action == "create":
                showtime = ShowTime.objects.create(fk_movie=movie, show_time=show_time)
            elif action == "update":
                showtime_id = request.POST.get('showtime_id')
                showtime = get_object_or_404(ShowTime, id=showtime_id, fk_movie__fk_theatre=theatre)
                showtime.show_time = show_time
                showtime.save()
                
                existing_dates = set(showtime.dates.values_list('date', flat=True))
                new_dates_to_add = new_dates - existing_dates  # Only add new dates

                for date in new_dates_to_add:
                    ShowtimeDate.objects.create(showtime=showtime, date=date)

            return JsonResponse({"success": True})

        # DELETE showtime
        elif action == "delete":
            showtime_id = request.POST.get('showtime_id')
            showtime = get_object_or_404(ShowTime, id=showtime_id, fk_movie__fk_theatre=theatre)
            showtime.delete()
            return JsonResponse({"success": True})

    return render(request, 'theatre/theatre_shows.html', {'movies': movies, 'showtimes': showtimes})

@require_POST
def get_showtime_dates(request, showtime_id):
    showtime = get_object_or_404(ShowTime, id=showtime_id)
    dates = list(showtime.dates.values_list('date', flat=True))
    return JsonResponse({"dates": dates})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ShowTime, ShowtimeDate

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ShowTime, ShowtimeDate

def remove_showtime_date(request, showtime_id, date_id):
    if request.method == "POST":
        showtime = get_object_or_404(ShowTime, id=showtime_id)
        date = get_object_or_404(ShowtimeDate, id=date_id)

        try:
            date.delete()  # Directly delete the date entry
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False}, status=400)











from .models import Seat, ShowTime

def create_seats(showtime):
    sections = ["X", "Y", "Z", "A"]
    rows = ["A", "B", "C", "D", "E"]
    seats_per_row = 5

    for section in sections:
        for row in rows:
            for seat_number in range(1, seats_per_row + 1):
                seat_id = f"{section}{row}{seat_number}"
                Seat.objects.get_or_create(fk_showtime=showtime, seat_number=seat_id)

    print("100 seats created successfully!")



from django.shortcuts import render, get_object_or_404, redirect
from .models import Seat

import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ShowTime, Seat, Booking, CustomUser
# If you use Django authentication, you can replace CustomUser.objects.first() with request.user
from django.shortcuts import render, get_object_or_404


from django.db.models import Min
from django.utils.timezone import now

from django.utils.timezone import now
from django.shortcuts import get_object_or_404, render
from .models import Seat, ShowTime, ShowtimeDate
import datetime

def seat_booking(request, showtime_id):
    showtime = get_object_or_404(ShowTime, id=showtime_id)

    # Fetch available dates
    available_dates = ShowtimeDate.objects.filter(
        showtime=showtime, date__gte=now().date()
    ).values_list("date", flat=True).distinct()

    # Get selected date from request
    selected_date_str = request.GET.get("date")
    selected_date = None
    if selected_date_str:
        try:
            selected_date = datetime.datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = None

    # Use the first available date if none is selected
    if not selected_date and available_dates:
        selected_date = available_dates[0]

    # Get showtime date object
    showtime_date = ShowtimeDate.objects.filter(showtime=showtime, date=selected_date).first()

    if showtime_date:
        booked_seats = Booking.objects.filter(
            fk_seat__fk_showtime=showtime,
            fk_seat__is_booked=True,
            booking_date=selected_date  # FIX: Filter by selected date
        ).values_list("fk_seat__seat_number", flat=True)
        
        seats = Seat.objects.filter(fk_showtime=showtime).order_by('seat_number')
    else:
        seats = []
        booked_seats = []

    return render(request, 'user/seat_booking.html', {
        'showtime': showtime,
        'seats': seats,
        'booked_seats': booked_seats,  # Fixed: Now filtered by date
        'available_dates': available_dates,
        'selected_date': selected_date
    })

from django.conf import settings
@csrf_exempt
def book_seat(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)
    
    seat_numbers = data.get("seat_numbers", [])
    showtime_id = data.get("showtime_id")
    selected_date = data.get("selected_date")
    booking_type = data.get("booking_type")
    payment_method = data.get("payment_method")
    
    if not seat_numbers or not showtime_id or not booking_type or not payment_method:
        return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)
    
    # Validate the showtime exists
    try:
        showtime = ShowTime.objects.get(id=showtime_id)
    except ShowTime.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Showtime not found"}, status=404)
    
    # Ensure user is authenticated
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"status": "error", "message": "User not authenticated"}, status=403)
    
    booked_seats = []
    for seat_number in seat_numbers:
        try:
            seat = Seat.objects.get(fk_showtime=showtime, seat_number=seat_number)
        except Seat.DoesNotExist:
            return JsonResponse({"status": "error", "message": f"Seat {seat_number} not found"}, status=404)
        
        if seat.is_booked:
            return JsonResponse({"status": "error", "message": f"Seat {seat_number} is already booked"}, status=400)
        
        # Create booking record with the correct user
        Booking.objects.create(
            fk_user=user,
            fk_seat=seat,
            booking_date=selected_date,
            booking_type=booking_type,
            payment_method=payment_method
        )
        # Mark the seat as booked
        seat.is_booked = True
        seat.booked_by = user
        seat.save()
        booked_seats.append(seat_number)
        print("Received Data:", data)
        subject = "Booking Confirmation"
        message = f"Dear {user.username},\n\nYou have successfully booked the following seats: {', '.join(booked_seats)} on {selected_date}.\n\nPayment Method: {payment_method}\nBooking Type: {booking_type}\n\nThank you for choosing our service!\n\nBest Regards,\nYour Booking Team"
        recipient_list = [user.email]

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    
    return JsonResponse({"status": "success", "message": f"Seats {booked_seats} booked successfully!"})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Booking

@login_required
def booking_history(request):
    PRICE_PER_SEAT = 50  # Set price per seat

    # Fetch booking records for the logged-in user, ordered by booking date and id
    bookings = Booking.objects.filter(fk_user=request.user).order_by('booking_date', 'id')

    # Group bookings by booking transaction using the booking ID
    grouped_bookings = {}
    for booking in bookings:
        key = (booking.booking_date, booking.fk_seat.fk_showtime_id, booking.id)  # Use ID to separate transactions
        if key not in grouped_bookings:
            grouped_bookings[key] = {"bookings": [], "total_amount": 0}
        
        grouped_bookings[key]["bookings"].append(booking)
        grouped_bookings[key]["total_amount"] += PRICE_PER_SEAT  # Calculate total price

    return render(request, 'user/booking_history.html', {
        'grouped_bookings': grouped_bookings
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Booking

@csrf_exempt
def cancel_booking(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            booking_id = data.get("booking_id")
            reason = data.get("reason")

            booking = Booking.objects.get(id=booking_id)
            
            # Ensure only flexi bookings can be cancelled
            if booking.booking_type != "flexi":
                return JsonResponse({"status": "error", "message": "Only flexi bookings can be cancelled."})

            booking.is_cancelled = True
            booking.cancellation_reason = reason
            booking.cancellation_status = "pending"
            booking.save()

            return JsonResponse({"status": "success", "message": "Cancellation request submitted successfully."})
        
        except Booking.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Booking not found."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request."})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Booking

@login_required
def theatre_admin_bookings(request):
    if request.user.role != 2:  # Ensure only theatre operators can access
        return redirect('home')  # Redirect non-theatre admins to home

    bookings = Booking.objects.all().order_by('-booking_date')
    return render(request, 'theatre/refund_requests.html', {'bookings': bookings})

@login_required
def approve_cancellation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user.role != 2:  # Ensure only theatre operators can approve
        return redirect('home')

    booking.cancellation_status = 'approved'
    booking.is_cancelled = True
    booking.save()
    subject = "Cancellation Successful - Refund Processed"
    message = f"Dear {booking.fk_user.username},\n\nYour cancellation has been approved, and ₹50 has been successfully refunded.\n\nThank you for using our service.\n\nBest Regards,\nYour Booking Team"
    recipient_list = [booking.fk_user.email]


    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    return redirect('theatre_admin_bookings')  # Redirect back to admin page


############################################################################################################################

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Booking

@login_required
def theatre_admin_bookings_details(request):
    if request.user.role != 2:
        return redirect('home')

    all_bookings = Booking.objects.select_related(
        'fk_user', 'fk_seat__fk_showtime__fk_movie'
    ).order_by('-booking_date')

    grouped_bookings = {}

    for booking in all_bookings:
        showtime = booking.fk_seat.fk_showtime if hasattr(booking.fk_seat, 'fk_showtime') else None
        movie = showtime.fk_movie if showtime and hasattr(showtime, 'fk_movie') else None
        booking_date = showtime.date if showtime and hasattr(showtime, 'date') else None

        key = (
            booking.fk_user.id,
            movie.id if movie else None,
            showtime.show_time if showtime else None,
            booking_date
        )

        if key not in grouped_bookings:
            grouped_bookings[key] = {
                'fk_user': booking.fk_user,
                'movie_name': movie.movie_name if movie else 'Unknown',
                'show_time': showtime.show_time if showtime else 'Unknown',
                'booking_date': booking.booking_date,
                'payment_methods': set(),
                'seats': [],
                'booking_id': booking.id
            }

        grouped_bookings[key]['payment_methods'].add(booking.payment_method)
        grouped_bookings[key]['seats'].append(booking.fk_seat)

    # Convert sets to lists for template compatibility
    for key in grouped_bookings:
        grouped_bookings[key]['payment_methods'] = list(grouped_bookings[key]['payment_methods'])

    return render(request, 'theatre/theatre_admin_bookings_details.html', {'bookings': grouped_bookings.values()})






# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from .models import Booking

# @login_required
# def theatre_admin_bookings_details(request):
#     if request.user.role != 2:  # Ensure only theatre operators can access
#         return redirect('home')  # Redirect non-theatre admins to home

#     # ✅ Fetch all bookings across all movies for that theatre admin
#     bookings = Booking.objects.select_related(
#         'fk_seat__fk_showtime__fk_movie__fk_theatre'
#     ).filter(
#         fk_seat__fk_showtime__fk_movie__fk_theatre__fk_user=request.user
#     ).order_by('-booking_date')

#     return render(request, 'theatre/theatre_admin_bookings_details.html', {'bookings': bookings})




# @login_required
# def theatre_admin_bookings_details(request):
#     if request.user.role != 2:  # Ensure only theatre operators can access
#         return redirect('home')  # Redirect non-theatre admins to home

#     bookings = Booking.objects.all().order_by('-booking_date')
#     return render(request, 'theatre/theatre_admin_bookings_details.html', {'bookings': bookings})





@login_required
def theatre_x(request):
    if request.user.role != 2:
        return render(request, 'error.html', {'message': 'Unauthorized access'})

    try:
        theatre_profile = Theatre_Profile.objects.get(fk_user=request.user)
    except Theatre_Profile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Theatre profile not found'})

    movies = Movie.objects.filter(fk_theatre=theatre_profile)

    movie_data = {}

    for movie in movies:
        showtimes = ShowTime.objects.filter(fk_movie=movie)  

        showtime_data = []
        for showtime in showtimes:
            available_seats = Seat.objects.filter(fk_showtime=showtime, is_booked=False)
            booked_seats = Seat.objects.filter(fk_showtime=showtime, is_booked=True)

            showtime_data.append({
                'show_id': showtime.id,
                'show_time': showtime.show_time,
                'available_seats_count': available_seats.count(),
                'booked_seats_count': booked_seats.count(),
                'available_seats_list': [seat.seat_number for seat in available_seats],
                'booked_seats_list': [seat.seat_number for seat in booked_seats]
            })

        movie_data[movie] = showtime_data

    return render(request, 'theatre/theatre_x.html', {'movie_data': movie_data})


# @login_required
# def theatre_x(request):
#     if request.user.role != 2:
#         return render(request, 'error.html', {'message': 'Unauthorized access'})

#     try:
#         theatre_profile = Theatre_Profile.objects.get(fk_user=request.user)
#     except Theatre_Profile.DoesNotExist:
#         return render(request, 'error.html', {'message': 'Theatre profile not found'})

#     movies = Movie.objects.filter(fk_theatre=theatre_profile)

#     movie_data = {}

#     for movie in movies:
#         showtimes = ShowTime.objects.filter(fk_movie=movie)  

#         showtime_data = []
#         for showtime in showtimes:
#             available_seats = Seat.objects.filter(fk_showtime=showtime, is_booked=False)
#             booked_seats = Seat.objects.filter(fk_showtime=showtime, is_booked=True)

#             showtime_data.append({
#                 'show_time': showtime.show_time,
#                 'available_seats_count': available_seats.count(),
#                 'booked_seats_count': booked_seats.count(),
#                 'available_seats_list': [seat.seat_number for seat in available_seats],
#                 'booked_seats_list': [seat.seat_number for seat in booked_seats]
#             })

#         movie_data[movie] = showtime_data

#     context = {
#         'movie_data': movie_data,
#     }
#     return render(request, 'theatre/theatre_x.html', context)




##########################################################

from django.shortcuts import render
from .models import Movie

def movies_list_x(request):
    query = request.GET.get('q', '')  # Get search query from URL
    if query:
        movies = Movie.objects.filter(movie_name__icontains=query)
    else:
        movies = Movie.objects.all()

    return render(request, 'user/movies_list.html', {'movies_list': movies, 'query': query})


def movie_detail_x(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    return render(request, 'user/movie_detail.html', {'movie': movie})