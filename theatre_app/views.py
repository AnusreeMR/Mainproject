from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout



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




from django.db.models import Count, Avg, F
from django.shortcuts import render
from .models import Booking, Movie

from django.db.models import Count, Avg, F
from django.shortcuts import render
from .models import Booking, Movie

from django.db.models import Count, Avg
from django.shortcuts import render
from .models import Booking, Movie

from django.db.models import Count, Avg
from django.shortcuts import render
from .models import Booking, Movie
from django.db.models import Count, Avg
from django.shortcuts import render
from .models import Booking, Movie

from django.shortcuts import render
from django.db.models import Count, Avg
from .models import Booking, Movie

from django.db.models import Count, Avg

from django.db.models import Count, Avg

def user_dashboard(request):
    user = request.user

    # Step 1: Get all movies with their average rating
    movies_list = Movie.objects.annotate(avg_rating=Avg('ratings__rating'))

    # Step 2: Get the user's booked movie IDs with counts
    booked_movies = Booking.objects.filter(fk_user=user) \
        .values('fk_seat__fk_showtime__fk_movie') \
        .annotate(booking_count=Count('id')) \
        .order_by('-booking_count')

    # Initialize recommended movies as empty queryset
    recommended_movies = Movie.objects.none()

    if booked_movies.exists():
        # Step 3: Get only movies booked more than once
        frequently_booked_movie_ids = [
            item['fk_seat__fk_showtime__fk_movie'] 
            for item in booked_movies 
            if item['booking_count'] > 1
        ]

        if frequently_booked_movie_ids:
            # Step 4: Analyze genres from frequently booked movies
            from collections import defaultdict
            genre_counts = defaultdict(int)
            
            freq_booked_movies = Movie.objects.filter(id__in=frequently_booked_movie_ids)
            for movie in freq_booked_movies:
                genres = [g.strip().lower() for g in movie.movie_genre.split(',')]
                for genre in genres:
                    genre_counts[genre] += 1

            if genre_counts:
                # Step 5: Get only genres that appear in multiple frequently booked movies
                popular_genres = [genre for genre, count in genre_counts.items() if count > 1]
                
                if popular_genres:
                    # Step 6: Find recommendations matching these popular genres
                    for genre in popular_genres:
                        genre_movies = Movie.objects.filter(movie_genre__icontains=genre)
                        recommended_movies = recommended_movies | genre_movies
                    
                    # Final filtering and ordering
                    all_booked_ids = booked_movies.values_list(
                        'fk_seat__fk_showtime__fk_movie', flat=True
                    ).distinct()
                    
                    recommended_movies = (
                        recommended_movies
                        .exclude(id__in=all_booked_ids)
                        .order_by('-movie_release_date')
                        .distinct()[:6]
                    )

    # Fallback if no recommendations from frequent bookings
    if not recommended_movies.exists():
        # Get all booked IDs for exclusion
        all_booked_ids = booked_movies.values_list(
            'fk_seat__fk_showtime__fk_movie', flat=True
        ).distinct()
        
        recommended_movies = (
            Movie.objects.all()
            .exclude(id__in=all_booked_ids)
            .order_by('-movie_release_date')[:6]
        )

    return render(request, 'user/user_dashboard.html', {
        'movies_list': movies_list,
        'recommended_movies': recommended_movies,
    })

# def user_dashboard(request):
#     user = request.user

#     # Step 1: Get the user's booked movie IDs
#     booked_movie_ids = Booking.objects.filter(fk_user=user).values_list(
#         'fk_seat__fk_showtime__fk_movie', flat=True
#     )

#     # Step 2: Find the count of each booked genre
#     booked_genres = (
#         Movie.objects.filter(id__in=booked_movie_ids)
#         .values('movie_genre')
#         .annotate(genre_count=Count('id'))
#         .order_by('-genre_count')  # Sort by most booked
#     )

#     recommended_movies = Movie.objects.none()  # Default empty queryset

#     if booked_genres.exists():  # Ensure there's booking history
#         # Step 3: Get the highest booking count
#         max_genre_count = booked_genres.first()['genre_count']

#         # Step 4: Filter out only the most booked genre(s)
#         most_watched_genres = [
#             genre['movie_genre'] for genre in booked_genres if genre['genre_count'] == max_genre_count
#         ]

#         print(f"Most Watched Genres: {most_watched_genres}")  # Debugging

#         # Step 5: Get only movies from the most watched genre(s)
#         recommended_movies = Movie.objects.filter(movie_genre__in=most_watched_genres)

#         # Step 6: Fetch newly added movies in that genre (even if not booked)
#         newly_added_movies = Movie.objects.filter(
#             movie_genre__in=most_watched_genres
#         ).exclude(id__in=booked_movie_ids)  # Exclude movies already booked
#         newly_added_movies = newly_added_movies.order_by('-movie_release_date')

#         print(f"Recommended Movies Before New Filter: {recommended_movies}")  # Debugging
#         print(f"Newly Added Movies: {newly_added_movies}")  # Debugging

#         # Step 7: Merge new movies with recommended movies
#         recommended_movies = (recommended_movies | newly_added_movies).distinct()
#     else:
#         # If no booking history, suggest only the latest movie
#         latest_movie = Movie.objects.all().order_by('-movie_release_date').first()
#         recommended_movies = [latest_movie] if latest_movie else []

#     # Step 8: Fetch all movies with their average rating
#     movies_list = Movie.objects.annotate(avg_rating=Avg('ratings__rating'))

#     return render(request, 'user/user_dashboard.html', {
#         'movies_list': movies_list,
#         'recommended_movies': recommended_movies,  # Movies from most booked genres + new movies from that genre
#     })


# def user_dashboard(request):
#     user = request.user

#     # Step 1: Get the user's booked movie IDs
#     booked_movie_ids = Booking.objects.filter(fk_user=user).values_list(
#         'fk_seat__fk_showtime__fk_movie', flat=True
#     )

#     # Step 2: Find the most booked genre(s)
#     booked_genres = (
#         Movie.objects.filter(id__in=booked_movie_ids)
#         .values('movie_genre')
#         .annotate(genre_count=Count('id'))
#         .order_by('-genre_count')
#     )

#     recommended_movies = Movie.objects.none()  # Default empty query

#     if booked_genres.exists():  # Ensure there's booking history
#         # Step 3: Find the most frequently booked genre(s)
#         max_genre_count = booked_genres.first()['genre_count']
#         most_watched_genres = [
#             genre['movie_genre'] for genre in booked_genres if genre['genre_count'] == max_genre_count
#         ]

#         print(f"Most Watched Genres: {most_watched_genres}")  # Debugging

#         # Step 4: Fetch ALL movies from the most booked genre(s)
#         recommended_movies = Movie.objects.filter(movie_genre__in=most_watched_genres)

#         # Step 5: Separate newly added movies (that haven't been booked)
#         newly_added_movies = recommended_movies.exclude(id__in=booked_movie_ids).order_by('-movie_release_date')

#         print(f"Recommended Movies Before New Filter: {recommended_movies}")  # Debugging
#         print(f"Newly Added Movies: {newly_added_movies}")  # Debugging

#         # If there are new movies, prioritize them in recommendations
#         if newly_added_movies.exists():
#             recommended_movies = newly_added_movies

#     # Step 6: Fetch all movies along with their average rating
#     movies_list = Movie.objects.annotate(avg_rating=Avg('ratings__rating'))

#     return render(request, 'user/user_dashboard.html', {
#         'movies_list': movies_list,
#         'recommended_movies': recommended_movies,  # Ensures movies are always recommended
#     })


# def user_dashboard(request):
#     user = request.user

#     # Fetch movie IDs booked by the user
#     booked_movies = Booking.objects.filter(fk_user=user).select_related('fk_seat__fk_showtime__fk_movie') \
#                                    .values_list('fk_seat__fk_showtime__fk_movie', flat=True).distinct()

#     print(f"Booked Movies: {booked_movies}")  # Debugging line to check booked movies

#     if not booked_movies:
#         # If no booking history, show only the most recently released movie
#         latest_movie = Movie.objects.all().order_by('-movie_release_date').first()  # Fetch the latest movie

#         # Wrap in a list to keep it consistent with querysets
#         recommended_movies = [latest_movie] if latest_movie else []
#     else:
#         # Find the most booked genres by the user
#         top_genres = (
#             Movie.objects.filter(id__in=booked_movies)
#             .values('movie_genre')
#             .annotate(genre_count=Count('id'))
#             .order_by('-genre_count')
#             .values_list('movie_genre', flat=True)
#         )

#         print(f"Top Genres: {top_genres}")  # Debugging line to check top genres

#         # Fetch recommended movies from the top genres
#         recommended_movies = Movie.objects.filter(movie_genre__in=top_genres)

#         print(f"Recommended Movies (before newly added check): {recommended_movies}")  # Debugging

#         # Fetch newly added movies that match the genres but exclude already booked ones
#         newly_added_movies = Movie.objects.filter(
#             movie_genre__in=top_genres
#         ).exclude(
#             id__in=booked_movies  # Exclude movies that the user has already booked
#         ).order_by('-movie_release_date')  # Sort by release date for newly added ones

#         print(f"Newly Added Movies: {newly_added_movies}")  # Debugging to check if this returns the expected data

#         # Combine both queries to get all recommended and newly added movies
#         combined_movies = recommended_movies | newly_added_movies

#         # Remove duplicates, in case a movie exists in both recommended and newly added lists
#         combined_movies = combined_movies.distinct()

#         print(f"Combined Movies: {combined_movies}")  # Debugging to check the final result

#     # Fetch all movies along with their average rating
#     movies_list = Movie.objects.annotate(avg_rating=Avg('ratings__rating'))  # Assuming `ratings` is the related name for the rating model

#     # Render the result
#     return render(request, 'user/user_dashboard.html', {
#         'movies_list': movies_list,
#         'recommended_movies': recommended_movies  # Pass combined recommended movies
#     })



# def user_dashboard(request):
#     user = request.user

#     # Fetch movies the user rated 5
#     top_rated_movies = Rating.objects.filter(user=user, rating=5).values_list('movie', flat=True)
#     print("User's 5-star movies:", top_rated_movies)  # Debugging

#     # Fetch recommended movies
#     recommended_movies = Movie.objects.annotate(
#         avg_rating=Avg('ratings__rating'),
#         total_ratings=Count('ratings')
#     ).filter(avg_rating__gte=3.5).exclude(id__in=top_rated_movies).order_by('-avg_rating', '-total_ratings')

#     print("Recommended Movies:", recommended_movies)  # Debugging

#     # Fetch all movies
#     movies_list = Movie.objects.annotate(
#         avg_rating=Avg('ratings__rating'),
#         total_ratings=Count('ratings')
#     ).order_by('-avg_rating', '-total_ratings')

#     return render(request, 'user/user_dashboard.html', {
#         'movies_list': movies_list,
#         'recommended_movies': recommended_movies
#     })


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
    try:
        theatre = Theatre_Profile.objects.get(id=theatre_id)  # ✅ Fetch from Theatre_Profile
        movies = Movie.objects.filter(fk_theatre=theatre)

        # Create a list of movies with their respective showtimes
        movies_with_showtimes = []
        for movie in movies:
            showtimes = ShowTime.objects.filter(fk_movie=movie)  # Get full ShowTime objects
            movies_with_showtimes.append({'movie': movie, 'showtimes': showtimes})

        return render(request, 'user/theatre_movies.html', {
            'theatre': theatre,
            'movies_with_showtimes': movies_with_showtimes
        })
    except Theatre_Profile.DoesNotExist:
        return render(request, 'user/theatre_movies.html', {
            'error_message': 'Theatre not found',
            'movies_with_showtimes': []
        })


# def theatre_movies(request, theatre_id):
#     movies = Movie.objects.filter(fk_theatre_id=theatre_id)
#     theatre = CustomUser.objects.get(id=theatre_id)

#     # Create a list of movies with their respective showtimes
#     movies_with_showtimes = []
#     for movie in movies:
#         showtimes = ShowTime.objects.filter(fk_movie=movie)  # Get full ShowTime objects
#         movies_with_showtimes.append({'movie': movie, 'showtimes': showtimes})

#     return render(request, 'user/theatre_movies.html', {
#         'theatre': theatre,
#         'movies_with_showtimes': movies_with_showtimes
#     })

# def theatre_movies(request, theatre_id):
#     try:
#         theatre = Theatre_Profile.objects.get(id=theatre_id)
#         movies = Movie.objects.filter(fk_theatre=theatre)

#         movies_with_showtimes = []

#         for movie in movies:
#             showtimes = ShowTime.objects.filter(fk_movie=movie)  # Get showtimes for the movie

#             # Group showtimes by screen number
#             showtimes_by_screen = {}
#             for showtime in showtimes:
#                 screen_number = movie.movie_screen  # Fetch screen number from the Movie model
#                 if screen_number not in showtimes_by_screen:
#                     showtimes_by_screen[screen_number] = []
#                 showtimes_by_screen[screen_number].append(showtime)

#             # ✅ Fix: Prevent IndexError by ensuring default_screen exists
#             default_screen = list(showtimes_by_screen.keys())[0] if showtimes_by_screen else None

#             movies_with_showtimes.append({
#                 'movie': movie,
#                 'showtimes_by_screen': showtimes_by_screen,
#                 'default_screen': default_screen,  # ✅ Set default screen properly
#             })

#         return render(request, 'user/theatre_movies.html', {
#             'theatre': theatre,
#             'movies_with_showtimes': movies_with_showtimes
#         })

#     except Theatre_Profile.DoesNotExist:
#         return render(request, 'user/theatre_movies.html', {
#             'error_message': 'Theatre not found',
#             'movies_with_showtimes': []
#         })



# def theatre_movies(request, theatre_id):
#     movies = Movie.objects.filter(fk_theatre_id=theatre_id)
#     theatre = CustomUser.objects.get(id=theatre_id)

#     # Create a list of movies with their respective showtimes
#     movies_with_showtimes = []
#     for movie in movies:
#         showtimes = ShowTime.objects.filter(fk_movie=movie)  # Get full ShowTime objects
#         movies_with_showtimes.append({'movie': movie, 'showtimes': showtimes})

#     return render(request, 'user/theatre_movies.html', {
#         'theatre': theatre,
#         'movies_with_showtimes': movies_with_showtimes
#     })


from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Theatre_Profile, Movie, ShowTime, ShowtimeDate
from datetime import datetime


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
            show_time_str = request.POST.get('show_time')  # Get time as string (e.g., '14:30')

            # Convert string to time object
            show_time = datetime.strptime(show_time_str, "%H:%M").time()

            new_dates = set(request.POST.getlist('showtime_dates[]'))  # Get selected dates
            
            movie = get_object_or_404(Movie, id=movie_id, fk_theatre=theatre)

            if action == "create":
                showtime = ShowTime.objects.create(fk_movie=movie, show_time=show_time)
            elif action == "update":
                showtime_id = request.POST.get('showtime_id')
                showtime = get_object_or_404(ShowTime, id=showtime_id, fk_movie__fk_theatre=theatre)
                showtime.show_time = show_time
                showtime.save()
                # Remove existing dates before adding new ones
                ShowtimeDate.objects.filter(showtime=showtime).delete()

            # Add new dates to ShowTimeDate model
            for date_str in new_dates:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                ShowtimeDate.objects.create(showtime=showtime, date=date_obj)

            return JsonResponse({"success": True})

        # DELETE showtime
        elif action == "delete":
            showtime_id = request.POST.get('showtime_id')
            showtime = get_object_or_404(ShowTime, id=showtime_id, fk_movie__fk_theatre=theatre)
            showtime.delete()
            return JsonResponse({"success": True})

    return render(request, 'theatre/theatre_shows.html', {'movies': movies, 'showtimes': showtimes})

# def theatre_shows(request):
#     if not request.user.is_authenticated or request.user.role != 2:  # Role 2 = Theatre Operator
#         return redirect('home')

#     try:
#         theatre = Theatre_Profile.objects.get(fk_user=request.user)
#         movies = Movie.objects.filter(fk_theatre=theatre)
#         showtimes = ShowTime.objects.filter(fk_movie__fk_theatre=theatre)
#     except Theatre_Profile.DoesNotExist:
#         movies = []
#         showtimes = []

#     if request.method == "POST":
#         action = request.POST.get('action')

#         # CREATE or UPDATE showtime
#         if action in ["create", "update"]:
#             movie_id = request.POST.get('fk_movie')
#             show_time_str = request.POST.get('show_time')  # Get time as string (e.g., '14:30')

#             # Convert string to time object
#             show_time = datetime.strptime(show_time_str, "%H:%M").time()

#             new_dates = set(request.POST.getlist('showtime_dates[]'))
            
#             movie = get_object_or_404(Movie, id=movie_id, fk_theatre=theatre)

#             if action == "create":
#                 showtime = ShowTime.objects.create(fk_movie=movie, show_time=show_time)
#             elif action == "update":
#                 showtime_id = request.POST.get('showtime_id')
#                 showtime = get_object_or_404(ShowTime, id=showtime_id, fk_movie__fk_theatre=theatre)
#                 showtime.show_time = show_time
#                 showtime.save()

#             return JsonResponse({"success": True})

#         # DELETE showtime
#         elif action == "delete":
#             showtime_id = request.POST.get('showtime_id')
#             showtime = get_object_or_404(ShowTime, id=showtime_id, fk_movie__fk_theatre=theatre)
#             showtime.delete()
#             return JsonResponse({"success": True})

#     return render(request, 'theatre/theatre_shows.html', {'movies': movies, 'showtimes': showtimes})


# def theatre_shows(request):
#     if not request.user.is_authenticated or request.user.role != 2:  # Role 2 = Theatre Operator
#         return redirect('home')

#     try:
#         theatre = Theatre_Profile.objects.get(fk_user=request.user)
#         movies = Movie.objects.filter(fk_theatre=theatre)
#         showtimes = ShowTime.objects.filter(fk_movie__fk_theatre=theatre)
#     except Theatre_Profile.DoesNotExist:
#         movies = []
#         showtimes = []

#     if request.method == "POST":
#         action = request.POST.get('action')

#         # CREATE or UPDATE showtime
#         if action in ["create", "update"]:
#             movie_id = request.POST.get('fk_movie')
#             show_time = request.POST.get('show_time')
#             new_dates = set(request.POST.getlist('showtime_dates[]'))
            
#             movie = get_object_or_404(Movie, id=movie_id, fk_theatre=theatre)

#             if action == "create":
#                 showtime = ShowTime.objects.create(fk_movie=movie, show_time=show_time)
#             elif action == "update":
#                 showtime_id = request.POST.get('showtime_id')
#                 showtime = get_object_or_404(ShowTime, id=showtime_id, fk_movie__fk_theatre=theatre)
#                 showtime.show_time = show_time
#                 showtime.save()
                
#                 existing_dates = set(showtime.dates.values_list('date', flat=True))
#                 new_dates_to_add = new_dates - existing_dates  # Only add new dates

#                 for date in new_dates_to_add:
#                     ShowtimeDate.objects.create(showtime=showtime, date=date)

#             return JsonResponse({"success": True})

#         # DELETE showtime
#         elif action == "delete":
#             showtime_id = request.POST.get('showtime_id')
#             showtime = get_object_or_404(ShowTime, id=showtime_id, fk_movie__fk_theatre=theatre)
#             showtime.delete()
#             return JsonResponse({"success": True})

#     return render(request, 'theatre/theatre_shows.html', {'movies': movies, 'showtimes': showtimes})


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ShowTime

def get_showtime_dates(request, showtime_id):
    showtime = get_object_or_404(ShowTime, id=showtime_id)
    
    dates = list(showtime.dates.values_list('date', flat=True))  

    # Convert time to string in "HH:MM" format
    showtime_time = showtime.show_time.strftime("%H:%M") if showtime.show_time else ""

    return JsonResponse({
        "dates": dates, 
        "time": showtime_time  # Send time in correct format
    })






# @require_POST
# def get_showtime_dates(request, showtime_id):
#     showtime = get_object_or_404(ShowTime, id=showtime_id)
#     dates = list(showtime.dates.values_list('date', flat=True))
#     return JsonResponse({"dates": dates})


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



from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.management import call_command
from io import StringIO
import sys

@require_POST
def generate_seats(request):
    if not request.user.is_authenticated or request.user.role != 2:  # Only theatre operators
        return JsonResponse({'success': False, 'message': 'Permission denied'})

    # Capture the output of the command
    output = StringIO()
    sys.stdout = output
    
    try:
        # Call the management command
        call_command('generate_seats')
        sys.stdout = sys.__stdout__
        return JsonResponse({'success': True, 'message': 'Seats generated successfully'})
    except Exception as e:
        sys.stdout = sys.__stdout__
        return JsonResponse({'success': False, 'message': str(e)})




############################################################################################################################



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localtime
from .models import Theatre_Profile, Booking, ShowtimeDate

@login_required
def theatre_admin_bookings_details(request):
    if request.user.role != 2:
        return redirect('home')

    try:
        theatre = Theatre_Profile.objects.get(fk_user=request.user)
    except Theatre_Profile.DoesNotExist:
        return redirect('home')

    all_bookings = Booking.objects.select_related(
        'fk_user', 'fk_seat__fk_showtime__fk_movie'
    ).filter(fk_seat__fk_showtime__fk_movie__fk_theatre=theatre).order_by('-booking_date')

    grouped_bookings = {}

    for booking in all_bookings:
        showtime = booking.fk_seat.fk_showtime if hasattr(booking.fk_seat, 'fk_showtime') else None
        movie = showtime.fk_movie if showtime and hasattr(showtime, 'fk_movie') else None

        # ✅ Fetch the correct show date
        show_date_obj = ShowtimeDate.objects.filter(showtime=showtime).first() if showtime else None
        show_date = show_date_obj.date if show_date_obj else None

        # ✅ Convert booking date to system's local time
        booking_date = localtime(booking.booking_date)

        key = (
            booking.fk_user.id,
            movie.id if movie else None,
            showtime.show_time if showtime else None,
            show_date  # ✅ Correct show date fetched
        )

        if key not in grouped_bookings:
            grouped_bookings[key] = {
                'fk_user': booking.fk_user,
                'movie_name': movie.movie_name if movie else 'Unknown',
                'show_time': showtime.show_time if showtime else 'Unknown',
                'show_date': show_date,  # ✅ Correctly assigned
                'booking_date': booking_date,  # ✅ Correctly assigned
                'payment_methods': set(),
                'seats': [],
                'booking_id': booking.id
            }

        grouped_bookings[key]['payment_methods'].add(booking.payment_method)
        grouped_bookings[key]['seats'].append(booking.fk_seat)

    for key in grouped_bookings:
        grouped_bookings[key]['payment_methods'] = list(grouped_bookings[key]['payment_methods'])

    return render(request, 'theatre/theatre_admin_bookings_details.html', {'bookings': grouped_bookings.values()})



#new
# @login_required
# def theatre_admin_bookings_details(request):
#     if request.user.role != 2:
#         return redirect('home')

#     try:
#         # Get the theatre profile of the logged-in theatre operator
#         theatre = Theatre_Profile.objects.get(fk_user=request.user)
#     except Theatre_Profile.DoesNotExist:
#         return redirect('home')  # Redirect if no theatre profile exists

#     # Filter bookings only for movies in this theatre
#     all_bookings = Booking.objects.select_related(
#         'fk_user', 'fk_seat__fk_showtime__fk_movie'
#     ).filter(fk_seat__fk_showtime__fk_movie__fk_theatre=theatre).order_by('-booking_date')

#     grouped_bookings = {}

#     for booking in all_bookings:
#         showtime = booking.fk_seat.fk_showtime if hasattr(booking.fk_seat, 'fk_showtime') else None
#         movie = showtime.fk_movie if showtime and hasattr(showtime, 'fk_movie') else None
#         booking_date = showtime.date if showtime and hasattr(showtime, 'date') else None

#         key = (
#             booking.fk_user.id,
#             movie.id if movie else None,
#             showtime.show_time if showtime else None,
#             booking_date
#         )

#         if key not in grouped_bookings:
#             grouped_bookings[key] = {
#                 'fk_user': booking.fk_user,
#                 'movie_name': movie.movie_name if movie else 'Unknown',
#                 'show_time': showtime.show_time if showtime else 'Unknown',
#                 'booking_date': booking.booking_date,
#                 'payment_methods': set(),
#                 'seats': [],
#                 'booking_id': booking.id
#             }

#         grouped_bookings[key]['payment_methods'].add(booking.payment_method)
#         grouped_bookings[key]['seats'].append(booking.fk_seat)

#     # Convert sets to lists for template compatibility
#     for key in grouped_bookings:
#         grouped_bookings[key]['payment_methods'] = list(grouped_bookings[key]['payment_methods'])

#     return render(request, 'theatre/theatre_admin_bookings_details.html', {'bookings': grouped_bookings.values()})


# @login_required
# def theatre_admin_bookings_details(request):
#     if request.user.role != 2:
#         return redirect('home')

#     all_bookings = Booking.objects.select_related(
#         'fk_user', 'fk_seat__fk_showtime__fk_movie'
#     ).order_by('-booking_date')

#     grouped_bookings = {}

#     for booking in all_bookings:
#         showtime = booking.fk_seat.fk_showtime if hasattr(booking.fk_seat, 'fk_showtime') else None
#         movie = showtime.fk_movie if showtime and hasattr(showtime, 'fk_movie') else None
#         booking_date = showtime.date if showtime and hasattr(showtime, 'date') else None

#         key = (
#             booking.fk_user.id,
#             movie.id if movie else None,
#             showtime.show_time if showtime else None,
#             booking_date
#         )

#         if key not in grouped_bookings:
#             grouped_bookings[key] = {
#                 'fk_user': booking.fk_user,
#                 'movie_name': movie.movie_name if movie else 'Unknown',
#                 'show_time': showtime.show_time if showtime else 'Unknown',
#                 'booking_date': booking.booking_date,
#                 'payment_methods': set(),
#                 'seats': [],
#                 'booking_id': booking.id
#             }

#         grouped_bookings[key]['payment_methods'].add(booking.payment_method)
#         grouped_bookings[key]['seats'].append(booking.fk_seat)

#     # Convert sets to lists for template compatibility
#     for key in grouped_bookings:
#         grouped_bookings[key]['payment_methods'] = list(grouped_bookings[key]['payment_methods'])

#     return render(request, 'theatre/theatre_admin_bookings_details.html', {'bookings': grouped_bookings.values()})






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


###########################################################

#rationg

@login_required
def submit_rating(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        rating_value = request.POST.get('rating')

        if movie_id and rating_value and 1 <= int(rating_value) <= 5:  # Validate rating
            movie = Movie.objects.get(id=movie_id)
            rating, created = Rating.objects.get_or_create(user=request.user, movie=movie)
            rating.rating = rating_value
            rating.save()
    
    return redirect('movies_list_x')


@login_required
def submit_comment(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        comment = request.POST.get('comment')

        if movie_id and comment:  # Validate comment
            movie = Movie.objects.get(id=movie_id)
            rating, created = Rating.objects.get_or_create(user=request.user, movie=movie)
            rating.comment = comment
            rating.save()

    return redirect('movies_list_x')



@login_required
def delete_comment(request, rating_id):
    rating = get_object_or_404(Rating, id=rating_id, user=request.user)
    if rating.comment:
        rating.comment = None  # Remove the comment only
        rating.save()
    return redirect('movies_list_x')  # Redirect to the movies list page


@login_required
def delete_rating(request, rating_id):
    rating = get_object_or_404(Rating, id=rating_id, user=request.user)
    rating.delete()  # Completely delete the rating
    return redirect('movies_list_x')


############################################################################################

@login_required
def user_complaints(request):
    # Fetch complaints of the logged-in user, ordered by latest first
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')

    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            Complaint.objects.create(user=request.user, message=message)
            return redirect('user_complaints')  # Adjust this based on your URL pattern

    return render(request, "user/user_complaints.html", {"complaints": complaints})


# @login_required
# def user_complaints(request):
#     # Fetch complaints of the logged-in user
#     complaints = Complaint.objects.filter(user=request.user)

#     if request.method == "POST":
#         message = request.POST.get("message")
#         if message:
#             Complaint.objects.create(user=request.user, message=message)
#             return redirect('user_complaints')  # Adjust this based on your URL pattern

#     return render(request, "user/user_complaints.html", {"complaints": complaints})



@login_required
def admin_complaints(request):
    if request.user.role != 1:  # Check if the user is an admin (role=1)
        return redirect('home')  # Adjust this based on your project's home URL

    all_complaints = Complaint.objects.filter(user__role=3).order_by('-created_at')

    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")
        reply = request.POST.get("reply")
        if complaint_id and reply:
            complaint = Complaint.objects.get(id=complaint_id)
            complaint.reply = reply
            complaint.save()
            return redirect('admin_complaints')

    return render(request, "admin/admin_complaints.html", {"complaints": all_complaints})

# @login_required
# def admin_complaints(request):
#     if request.user.role != 1:  # Check if the user is an admin (role=1)
#         return redirect('home')  # Adjust this based on your project's home URL

#     all_complaints = Complaint.objects.filter(user__role=3)

#     if request.method == "POST":
#         complaint_id = request.POST.get("complaint_id")
#         reply = request.POST.get("reply")
#         if complaint_id and reply:
#             complaint = Complaint.objects.get(id=complaint_id)
#             complaint.reply = reply
#             complaint.save()
#             return redirect('admin_complaints')

#     return render(request, "admin/admin_complaints.html", {"complaints": all_complaints})


@login_required
def theatre_to_admin_complaints(request):
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')

    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            Complaint.objects.create(user=request.user, message=message)
            return redirect('theatre_to_admin_complaints')  

    return render(request, "theatre/theatre_to_admin_complaints.html", {"complaints": complaints})


# @login_required
# def theatre_to_admin_complaints(request):
#     # Fetch complaints of the logged-in user
#     complaints = Complaint.objects.filter(user=request.user)

#     if request.method == "POST":
#         message = request.POST.get("message")
#         if message:
#             Complaint.objects.create(user=request.user, message=message)
#             return redirect('theatre_to_admin_complaints')  # Adjust this based on your URL pattern

#     return render(request, "theatre/theatre_to_admin_complaints.html", {"complaints": complaints})


@login_required
def list_theatre_to_admin_complaints_list(request):
    if request.user.role != 1:  
        return redirect('home')  

    all_complaints = Complaint.objects.filter(user__role=2).order_by('-created_at')

    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")
        reply = request.POST.get("reply")
        if complaint_id and reply:
            complaint = Complaint.objects.get(id=complaint_id)
            complaint.reply = reply
            complaint.save()
            return redirect('list_theatre_to_admin_complaints_list')

    return render(request, "admin/list_theatre_to_admin_complaints_list.html", {"complaints": all_complaints})


# @login_required
# def list_theatre_to_admin_complaints_list(request):
#     if request.user.role != 1:  # Check if the user is an admin (role=1)
#         return redirect('home')  # Adjust this based on your project's home URL

#     all_complaints = Complaint.objects.filter(user__role=2)

#     if request.method == "POST":
#         complaint_id = request.POST.get("complaint_id")
#         reply = request.POST.get("reply")
#         if complaint_id and reply:
#             complaint = Complaint.objects.get(id=complaint_id)
#             complaint.reply = reply
#             complaint.save()
#             return redirect('list_theatre_to_admin_complaints_list')

#     return render(request, "admin/list_theatre_to_admin_complaints_list.html", {"complaints": all_complaints})


############################################################################################

@login_required
def user_theatre_complaints(request):
    complaints = TheatreComplaint.objects.filter(user=request.user).order_by('-created_at')
    theatres = Theatre_Profile.objects.all()

    if request.method == "POST":
        theatre_id = request.POST.get("theatre_id")
        message = request.POST.get("message")
        if theatre_id and message:
            theatre = Theatre_Profile.objects.get(id=theatre_id)
            TheatreComplaint.objects.create(user=request.user, theatre=theatre, message=message)
            return redirect('user_theatre_complaints')

    return render(request, "user/user_theatre_complaints.html", {"complaints": complaints, "theatres": theatres})


# @login_required
# def user_theatre_complaints(request):
#     complaints = TheatreComplaint.objects.filter(user=request.user)
#     theatres = Theatre_Profile.objects.all()

#     if request.method == "POST":
#         theatre_id = request.POST.get("theatre_id")
#         message = request.POST.get("message")
#         if theatre_id and message:
#             theatre = Theatre_Profile.objects.get(id=theatre_id)
#             TheatreComplaint.objects.create(user=request.user, theatre=theatre, message=message)
#             return redirect('user_theatre_complaints')

#     return render(request, "user/user_theatre_complaints.html", {"complaints": complaints, "theatres": theatres})

##############################################

@login_required
def list_user_complaints_to_theatre(request):
    try:
        theatre = Theatre_Profile.objects.get(fk_user=request.user)
    except Theatre_Profile.DoesNotExist:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('theatre_operator_dashboard')

    complaints = TheatreComplaint.objects.filter(theatre=theatre).order_by('-created_at')

    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        reply = request.POST.get('reply')

        try:
            complaint = TheatreComplaint.objects.get(id=complaint_id, theatre=theatre)
            complaint.reply = reply
            complaint.save()
            messages.success(request, "Reply sent successfully.")
        except TheatreComplaint.DoesNotExist:
            messages.error(request, "Invalid complaint.")

    return render(request, 'theatre/list_complaints.html', {'complaints': complaints})

# @login_required
# def list_user_complaints_to_theatre(request):
#     try:
#         theatre = Theatre_Profile.objects.get(fk_user=request.user)
#     except Theatre_Profile.DoesNotExist:
#         messages.error(request, "You are not authorized to view this page.")
#         return redirect('theatre_operator_dashboard')

#     # Fetch complaints related to this theatre
#     complaints = TheatreComplaint.objects.filter(theatre=theatre)

#     if request.method == 'POST':
#         complaint_id = request.POST.get('complaint_id')
#         reply = request.POST.get('reply')

#         try:
#             complaint = TheatreComplaint.objects.get(id=complaint_id, theatre=theatre)
#             complaint.reply = reply
#             complaint.save()
#             messages.success(request, "Reply sent successfully.")
#         except TheatreComplaint.DoesNotExist:
#             messages.error(request, "Invalid complaint.")

#     return render(request, 'theatre/list_complaints.html', {'complaints': complaints})



##################################################


import json
import logging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from .models import ShowTime, Seat, Booking, ShowtimeDate

logger = logging.getLogger(__name__)


# View for selecting and displaying available seats
def seat_booking(request, showtime_id):
    showtime = get_object_or_404(ShowTime, id=showtime_id)

    # Fetch available dates for the showtime
    available_dates = ShowtimeDate.objects.filter(
        showtime=showtime, date__gte=now().date()
    ).values_list("date", flat=True).distinct()

    # Get selected date from request
    selected_date_str = request.GET.get("date")
    selected_date = None
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = None

    # Use the first available date if none is selected
    if not selected_date and available_dates.exists():
        selected_date = available_dates[0]

    # Get showtime date object
    showtime_date = ShowtimeDate.objects.filter(showtime=showtime, date=selected_date).first()

    if showtime_date:
        booked_seats = Booking.objects.filter(
            fk_seat__fk_showtime=showtime,
            booking_date=selected_date
        ).values_list("fk_seat__seat_number", flat=True)

        seats = Seat.objects.filter(fk_showtime=showtime).order_by('seat_number')
    else:
        seats = []
        booked_seats = []

    return render(request, 'user/seat_booking.html', {
        'showtime': showtime,
        'seats': seats,
        'booked_seats': booked_seats,
        'available_dates': available_dates,
        'selected_date': selected_date
    })

from datetime import datetime
# View for booking selected seats
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
    selected_date_str = data.get("selected_date")
    booking_type = data.get("booking_type")
    payment_method = data.get("payment_method")

    # Validate required fields
    if not seat_numbers or not showtime_id or not booking_type or not payment_method or not selected_date_str:
        return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)

    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()

    except ValueError:
        return JsonResponse({"status": "error", "message": "Invalid date format"}, status=400)

    # Validate showtime exists
    showtime = get_object_or_404(ShowTime, id=showtime_id)

    # Ensure user is authenticated
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"status": "error", "message": "User not authenticated"}, status=403)

    booked_seats = []
    errors = []

    # Atomic transaction for booking multiple seats
    with transaction.atomic():
        for seat_number in seat_numbers:
            try:
                # Check exact seat with full name
                seat = Seat.objects.select_for_update().get(
                    fk_showtime=showtime,
                    seat_number=seat_number
                )
            except Seat.DoesNotExist:
                errors.append(f"Seat {seat_number} not found.")
                continue

            # Check if seat is already booked for selected date
            existing_booking = Booking.objects.filter(
                fk_seat=seat,
                booking_date=selected_date
            ).exists()

            if existing_booking:
                errors.append(f"Seat {seat_number} is already booked.")
                continue

            # Create booking record
            Booking.objects.create(
                fk_user=user,
                fk_seat=seat,
                booking_date=selected_date,
                booking_type=booking_type,
                payment_method=payment_method
            )

            # Mark the seat as booked
            seat.is_booked = True
            seat.save()
            booked_seats.append(seat_number)

    # Handle partial booking errors
    if errors:
        return JsonResponse({
            "status": "partial_success",
            "message": f"Some seats couldn't be booked: {', '.join(errors)}",
            "booked_seats": booked_seats
        }, status=207)

    # No seats booked scenario
    if not booked_seats:
        return JsonResponse({"status": "error", "message": "No seats were booked"}, status=400)

    # Send booking confirmation email
    try:
        subject = "Booking Confirmation"
        message = (
            f"Dear {user.username},\n\n"
            f"You have successfully booked the following seats: {', '.join(booked_seats)} on {selected_date}.\n\n"
            f"Payment Method: {payment_method}\n"
            f"Booking Type: {booking_type}\n\n"
            "Thank you for choosing our service!"
        )
        recipient_list = [user.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}", exc_info=True)

    # Successful booking response
    return JsonResponse({
        "status": "success",
        "message": f"Seats {', '.join(booked_seats)} booked successfully!"
    })




######################################################################################################
######################################################################################################
######################################################################################################



from django.utils.timezone import localtime


import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Booking

from django.utils import timezone



from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from .models import Booking, ShowtimeDate
import json

from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking, ShowtimeDate

from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking, ShowtimeDate

from datetime import datetime, timedelta
from django.utils import timezone

def booking_history(request):
    user = request.user
    now = timezone.localtime(timezone.now())

    bookings = Booking.objects.filter(fk_user=user).select_related(
        "fk_seat__fk_showtime",
        "fk_seat__fk_showtime__fk_movie"
    ).order_by("-booking_date").all()

    grouped_bookings = {}

    for booking in bookings:
        booking_date = timezone.localtime(booking.booking_date).date()

        showtime_obj = booking.fk_seat.fk_showtime
        showtime_date = ShowtimeDate.objects.filter(showtime=showtime_obj).order_by("date").first()
        movie_name = showtime_obj.fk_movie.movie_name
        show_time = showtime_obj.show_time  # Correctly using the showtime

        # New grouping format: (movie_name, show_date, show_time, booking_type)
        grouping_key = (movie_name, showtime_date.date if showtime_date else None, show_time, booking.booking_type)

        if grouping_key not in grouped_bookings:
            grouped_bookings[grouping_key] = {
                "bookings": [],
                "total_amount": 0,
                "movie_name": movie_name,
                "show_time": show_time,
                "show_date": showtime_date.date if showtime_date else None,
                "booking_date": booking_date,
                "show_cancel_button": False,
                "is_expired": False,
                "seats": [],
            }

        grouped_bookings[grouping_key]["bookings"].append(booking)
        grouped_bookings[grouping_key]["seats"].append(booking.fk_seat.seat_number)

        amount = 175 if booking.booking_type == "flexi" else 100
        grouped_bookings[grouping_key]["total_amount"] += amount

        # Handle cancellation for flexi tickets
        if showtime_date and booking.booking_type == "flexi" and not booking.is_cancelled:
            show_datetime_str = f"{showtime_date.date.strftime('%Y-%m-%d')} {show_time}"
            
            try:
                # Try format with seconds
                show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    # Try format without seconds
                    show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    # Try AM/PM format
                    show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %I:%M %p")

            show_datetime = timezone.make_aware(show_datetime_naive, timezone.get_current_timezone())
            cancellation_end = show_datetime + timedelta(hours=3)

            if now >= show_datetime:
                grouped_bookings[grouping_key]["show_cancel_button"] = True  

            if now > cancellation_end:
                grouped_bookings[grouping_key]["is_expired"] = True  

    return render(request, "user/booking_history.html", {
        "grouped_bookings": grouped_bookings,
        "now": now,
    })


# def booking_history(request):
#     user = request.user
#     now = timezone.localtime(timezone.now())

#     bookings = Booking.objects.filter(fk_user=user).select_related(
#         "fk_seat__fk_showtime",
#         "fk_seat__fk_showtime__fk_movie"
#     ).order_by("-booking_date").all()

#     grouped_bookings = {}

#     for booking in bookings:
#         booking_date = timezone.localtime(booking.booking_date).date()

#         showtime_obj = booking.fk_seat.fk_showtime
#         showtime_date = ShowtimeDate.objects.filter(showtime=showtime_obj).order_by("date").first()
#         movie_name = showtime_obj.fk_movie.movie_name
#         show_time = showtime_obj.show_time  # Correctly using the showtime

#         # New grouping format: (movie_name, show_date, show_time, booking_type)
#         grouping_key = (movie_name, showtime_date.date if showtime_date else None, show_time, booking.booking_type)

#         if grouping_key not in grouped_bookings:
#             grouped_bookings[grouping_key] = {
#                 "bookings": [],
#                 "total_amount": 0,
#                 "movie_name": movie_name,
#                 "show_time": show_time,
#                 "show_date": showtime_date.date if showtime_date else None,
#                 "booking_date": booking_date,
#                 "show_cancel_button": False,
#                 "is_expired": False,
#                 "seats": [],
#             }

#         grouped_bookings[grouping_key]["bookings"].append(booking)
#         grouped_bookings[grouping_key]["seats"].append(booking.fk_seat.seat_number)

#         amount = 175 if booking.booking_type == "flexi" else 100
#         grouped_bookings[grouping_key]["total_amount"] += amount

#         # Handle cancellation for flexi tickets
#         if showtime_date and booking.booking_type == "flexi" and not booking.is_cancelled:
#             show_datetime_str = f"{showtime_date.date.strftime('%Y-%m-%d')} {show_time}"
            
#             try:
#                 show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %I:%M %p")
#             except ValueError:
#                 show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %H:%M")

#             show_datetime = timezone.make_aware(show_datetime_naive, timezone.get_current_timezone())
#             cancellation_end = show_datetime + timedelta(hours=3)

#             if now >= show_datetime:
#                 grouped_bookings[grouping_key]["show_cancel_button"] = True  

#             if now > cancellation_end:
#                 grouped_bookings[grouping_key]["is_expired"] = True  

#     return render(request, "user/booking_history.html", {
#         "grouped_bookings": grouped_bookings,
#         "now": now,
#     })



#new code
# def booking_history(request):
#     user = request.user
#     now = timezone.localtime(timezone.now())

#     bookings = Booking.objects.filter(fk_user=user).select_related(
#         "fk_seat__fk_showtime",
#         "fk_seat__fk_showtime__fk_movie"
#     ).order_by("-booking_date").all()  

#     grouped_bookings = {}
#     for booking in bookings:
#         booking_date = timezone.localtime(booking.booking_date).date()

#         showtime_obj = booking.fk_seat.fk_showtime
#         showtime_date = ShowtimeDate.objects.filter(showtime=showtime_obj).order_by("date").first()
#         movie_name = showtime_obj.fk_movie.movie_name
#         show_time = showtime_obj.show_time  # Ensure correct time grouping

#         grouping_key = (movie_name, showtime_date.date if showtime_date else None, show_time, booking_date)

#         if grouping_key not in grouped_bookings:
#             grouped_bookings[grouping_key] = {
#                 "bookings": [],
#                 "total_amount": 0,
#                 "movie_name": movie_name,
#                 "show_time": show_time,
#                 "show_date": showtime_date.date if showtime_date else None,
#                 "booking_date": booking_date,
#                 "show_cancel_button": False,
#                 "is_expired": False,
#             }

#         grouped_bookings[grouping_key]["bookings"].append(booking)
#         amount = 125 if booking.booking_type == "flexi" else 100
#         grouped_bookings[grouping_key]["total_amount"] += amount

#         # Handling flexi ticket cancellations and expiry
#         if showtime_date and booking.booking_type == "flexi" and not booking.is_cancelled:
#             show_datetime_str = f"{showtime_date.date.strftime('%Y-%m-%d')} {show_time}"
            
#             try:
#                 show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %I:%M %p")
#             except ValueError:
#                 show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %H:%M")

#             show_datetime = timezone.make_aware(show_datetime_naive, timezone.get_current_timezone())
#             cancellation_end = show_datetime + timedelta(hours=3)

#             if now >= show_datetime:
#                 grouped_bookings[grouping_key]["show_cancel_button"] = True  

#             if now > cancellation_end:
#                 grouped_bookings[grouping_key]["is_expired"] = True  

#     return render(request, "user/booking_history.html", {
#         "grouped_bookings": grouped_bookings,
#         "now": now,
#     })



# def booking_history(request):
#     user = request.user
#     now = timezone.localtime(timezone.now())  # Convert to local timezone

#     # Get all bookings for the logged-in user
#     bookings = Booking.objects.filter(fk_user=user).select_related(
#         "fk_seat__fk_showtime",
#         "fk_seat__fk_showtime__fk_movie"
#     ).order_by("-booking_date")

#     grouped_bookings = {}
#     for booking in bookings:
#         # Group by booking date
#         booking_date = booking.booking_date.date()

#         if booking_date not in grouped_bookings:
#             grouped_bookings[booking_date] = {
#                 "bookings": [],
#                 "total_amount": 0,
#                 "movie_name": booking.fk_seat.fk_showtime.fk_movie.movie_name,
#                 "show_time": booking.fk_seat.fk_showtime.show_time,
#                 "show_date": ShowtimeDate.objects.filter(showtime=booking.fk_seat.fk_showtime).first().date,
#                 "show_cancel_button": False,
#             }

#         # Add booking to the group
#         grouped_bookings[booking_date]["bookings"].append(booking)

#         # Dynamically calculate amount based on booking type
#         amount = 125 if booking.booking_type == "flexi" else 100
#         grouped_bookings[booking_date]["total_amount"] += amount

#         # Determine if cancel button should be shown
#         showtime_date = ShowtimeDate.objects.filter(showtime=booking.fk_seat.fk_showtime).first()
#         if showtime_date and not booking.is_cancelled and booking.booking_type == "flexi":
#             show_datetime_str = f"{showtime_date.date.strftime('%Y-%m-%d')} {booking.fk_seat.fk_showtime.show_time}"

#             try:
#                 show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %I:%M %p")
#             except ValueError:
#                 show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %H:%M")

#             show_datetime = timezone.make_aware(show_datetime_naive, timezone.get_current_timezone())
#             cancellation_end = show_datetime + timedelta(hours=3)

#             if show_datetime <= now <= cancellation_end:
#                 grouped_bookings[booking_date]["show_cancel_button"] = True

#     return render(request, "user/booking_history.html", {
#         "grouped_bookings": grouped_bookings,
#         "now": now,
#     })

# def auto_cancel_expired_bookings():
#     now = timezone.now()
    
#     expired_bookings = Booking.objects.filter(
#         is_cancelled=False,
#         fk_seat__fk_showtime__show_time__lt=now.strftime('%I:%M %p')
#     )

#     for booking in expired_bookings:
#         booking.is_cancelled = True
#         booking.cancellation_status = "auto"
#         booking.save()




from django.shortcuts import render, redirect
from .models import Booking, Theatre_Profile, Movie

from django.shortcuts import render, redirect
from .models import Booking, Theatre_Profile

@login_required
def theatre_admin_bookings(request):
    if request.user.role != 2:  # Ensure only theatre operators access this
        return redirect('home')

    try:
        # Get the theatre linked to the logged-in theatre operator
        theatre = Theatre_Profile.objects.get(fk_user=request.user)
    except Theatre_Profile.DoesNotExist:
        return redirect('home')  # If no theatre, redirect

    # Fetch only the bookings for this theatre
    bookings = Booking.objects.filter(
        fk_seat__fk_showtime__fk_movie__fk_theatre=theatre
    ).distinct()

    return render(request, 'theatre/refund_requests.html', {'bookings': bookings})




# @login_required
# def theatre_admin_bookings(request):
#     if request.user.role != 2:  # Ensure only theatre operators can access
#         return redirect('home')  # Redirect non-theatre admins to home

#     bookings = Booking.objects.all().order_by('-booking_date')
#     return render(request, 'theatre/refund_requests.html', {'bookings': bookings})



@csrf_exempt

def cancel_booking(request, booking_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            reason = data.get("reason")

            # Get the booking by ID and ensure it's the correct user
            booking = Booking.objects.get(id=booking_id, fk_user=request.user)

            # Check if booking is Flexi and not already cancelled
            if booking.booking_type != "flexi" or booking.cancellation_status != "none":
                return JsonResponse({"status": "error", "message": "Only uncancelled flexi bookings can be cancelled."})

            # Get related ShowtimeDate
            showtime_date = ShowtimeDate.objects.filter(showtime=booking.fk_seat.fk_showtime).first()

            if not showtime_date:
                return JsonResponse({"status": "error", "message": "Show date not found."})

            # Calculate cancellation time and refund percentage
            now = timezone.now()
            show_datetime_str = f"{showtime_date.date.strftime('%Y-%m-%d')} {booking.fk_seat.fk_showtime.show_time}"
            try:
                show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %I:%M %p")
            except ValueError:
                show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %H:%M")
            
            show_datetime = timezone.make_aware(show_datetime_naive, timezone.get_current_timezone())
            
            # Check if cancellation is within allowed window (3 hours after showtime)
            if not (show_datetime <= now <= show_datetime + timedelta(hours=3)):
                return JsonResponse({"status": "error", "message": "Cancellation window has expired. Cannot cancel this booking."})

            # Calculate time difference and refund percentage
            time_diff = now - show_datetime
            minutes_diff = time_diff.total_seconds() / 60
            
            if minutes_diff <= 30:
                refund_percentage = 75
            elif minutes_diff <= 60:
                refund_percentage = 50
            else:
                refund_percentage = 25

            # Store refund percentage in cancellation reason
            booking.cancellation_reason = f"{reason} (Refund: {refund_percentage}%)"
            booking.cancellation_status = "pending"  # Change status to "pending"
            booking.save()

            return JsonResponse({
                "status": "success", 
                "message": f"Cancellation for seat {booking.fk_seat.seat_number} submitted successfully.",
                "refund_percentage": refund_percentage
            })

        except Booking.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Booking not found."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request."})




# @csrf_exempt
# def cancel_booking(request, booking_id):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             reason = data.get("reason")

#             # Get the booking by ID
#             booking = Booking.objects.get(id=booking_id, fk_user=request.user)

#             # Check if booking is Flexi and not already cancelled
#             if booking.booking_type != "flexi" or booking.is_cancelled:
#                 return JsonResponse({"status": "error", "message": "Only uncancelled flexi bookings can be cancelled."})

#             # Get related ShowtimeDate
#             showtime_date = ShowtimeDate.objects.filter(showtime=booking.fk_seat.fk_showtime).first()

#             if not showtime_date:
#                 return JsonResponse({"status": "error", "message": "Show date not found."})

#             # Calculate cancellation time and refund percentage
#             now = timezone.now()
#             show_datetime_str = f"{showtime_date.date.strftime('%Y-%m-%d')} {booking.fk_seat.fk_showtime.show_time}"
#             try:
#                 show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %I:%M %p")
#             except ValueError:
#                 show_datetime_naive = datetime.strptime(show_datetime_str, "%Y-%m-%d %H:%M")
            
#             show_datetime = timezone.make_aware(show_datetime_naive, timezone.get_current_timezone())
            
#             # Check if cancellation is within allowed window (3 hours after showtime)
#             if not (show_datetime <= now <= show_datetime + timedelta(hours=3)):
#                 return JsonResponse({"status": "error", "message": "Cancellation window has expired. Cannot cancel this booking."})

#             # Calculate time difference and refund percentage
#             time_diff = now - show_datetime
#             minutes_diff = time_diff.total_seconds() / 60
            
#             if minutes_diff <= 30:
#                 refund_percentage = 75
#             elif minutes_diff <= 60:
#                 refund_percentage = 50
#             else:
#                 refund_percentage = 25

#             # Store refund percentage in cancellation reason
#             booking.is_cancelled = True
#             booking.cancellation_reason = f"{reason} (Refund: {refund_percentage}%)"
#             booking.cancellation_status = "pending"
#             booking.save()

#             return JsonResponse({
#                 "status": "success", 
#                 "message": f"Cancellation for seat {booking.fk_seat.seat_number} submitted successfully.",
#                 "refund_percentage": refund_percentage
#             })

#         except Booking.DoesNotExist:
#             return JsonResponse({"status": "error", "message": "Booking not found."})
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)})

#     return JsonResponse({"status": "error", "message": "Invalid request."})


@login_required
def approve_cancellation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Only theatre admin (role 2) can approve cancellations
    if request.user.role != 2:
        return redirect('home')

    # Parse refund percentage from cancellation reason
    refund_percentage = 0
    if booking.cancellation_reason and "(Refund:" in booking.cancellation_reason:
        try:
            refund_part = booking.cancellation_reason.split("(Refund:")[1]
            refund_percentage = int(refund_part.split("%)")[0].strip())
        except (IndexError, ValueError):
            pass

    # Calculate refund amount (assuming seat price is 125)
    seat_price = 175
    refund_amount = (refund_percentage / 100) * seat_price

    # Update booking status
    booking.cancellation_status = 'approved'  # Change status to "approved"
    booking.is_cancelled = True  # Now set as cancelled only after admin approval
    booking.save()

    # Update seat status to Available
    seat = booking.fk_seat
    seat.is_booked = False
    seat.booked_by = None
    seat.save(update_fields=["is_booked", "booked_by"])

    # Clear the booking reference from the seat if exists
    if hasattr(seat, 'booking'):
        seat.booking.delete()

    # Send confirmation email to user with refund details
    subject = "Cancellation Approved - Refund Processed"
    message = (
        f"Dear {booking.fk_user.username},\n\n"
        f"Your cancellation has been approved.\n"
        f"Refund Amount: ₹{refund_amount:.2f} ({refund_percentage}% of ₹{seat_price})\n"
        "The amount will be credited to your original payment method within 3-5 business days.\n\n"
        "Thank you for using our service.\n\n"
        "Best Regards,\nYour Booking Team"
    )
    recipient_list = [booking.fk_user.email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    # Redirect back to theatre admin bookings page
    return redirect('theatre_admin_bookings')



# @login_required
# def approve_cancellation(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id)

#     # Only theatre admin (role 2) can approve cancellations
#     if request.user.role != 2:
#         return redirect('home')

#     # Parse refund percentage from cancellation reason
#     refund_percentage = 0
#     if booking.cancellation_reason and "(Refund:" in booking.cancellation_reason:
#         try:
#             refund_part = booking.cancellation_reason.split("(Refund:")[1]
#             refund_percentage = int(refund_part.split("%)")[0].strip())
#         except (IndexError, ValueError):
#             pass

#     # Calculate refund amount (assuming seat price is 125)
#     seat_price = 175
#     refund_amount = (refund_percentage / 100) * seat_price

#     # Update booking status
#     booking.cancellation_status = 'approved'
#     booking.is_cancelled = True
#     booking.save()

#     # Update seat status to Available
#     seat = booking.fk_seat
#     seat.is_booked = False
#     seat.booked_by = None
#     seat.save(update_fields=["is_booked", "booked_by"])

#     # Clear the booking reference from the seat if exists
#     if hasattr(seat, 'booking'):
#         seat.booking.delete()

#     # Send confirmation email to user with refund details
#     subject = "Cancellation Approved - Refund Processed"
#     message = (
#         f"Dear {booking.fk_user.username},\n\n"
#         f"Your cancellation has been approved.\n"
#         f"Refund Amount: ₹{refund_amount:.2f} ({refund_percentage}% of ₹{seat_price})\n"
#         "The amount will be credited to your original payment method within 3-5 business days.\n\n"
#         "Thank you for using our service.\n\n"
#         "Best Regards,\nYour Booking Team"
#     )
#     recipient_list = [booking.fk_user.email]
#     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

#     # Redirect back to theatre admin bookings page
#     return redirect('theatre_admin_bookings')


from django.db.models import Avg

def user_theatre_list(request):
    theatres = Theatre_Profile.objects.all().annotate(avg_rating=Avg('tratings__rating'))
    return render(request, 'user/user_theatre_list.html', {'theatres': theatres})

@login_required
def submit_theatre_rating(request):
    if request.method == 'POST':
        theatre_id = request.POST.get('theatre_id')
        rating_value = request.POST.get('rating')

        if theatre_id and rating_value and 1 <= int(rating_value) <= 5:
            theatre = get_object_or_404(Theatre_Profile, id=theatre_id)
            rating, created = Theatre_Rating.objects.get_or_create(user=request.user, theatre=theatre)
            rating.rating = rating_value
            rating.save()

    return redirect('user_theatre_list')



####################################################################

def admin_view_theatre_rating(request):
    if request.user.role != 1:  # Ensure only admin can access
        return redirect('home')

    theatre_ratings = Theatre_Rating.objects.all().order_by('-rating', '-created_at')  # Highest rated first
    return render(request, 'admin/admin_view_theatre_rating.html', {'theatre_ratings': theatre_ratings})


def admin_view_movie_rating(request):
    if request.user.role != 1:  # Ensure only admin can access
        return redirect('home') 

    movie_ratings = Rating.objects.all().order_by('-rating', '-created_at')  # Highest rated first
    return render(request, 'admin/admin_view_movie_rating.html', {'movie_ratings': movie_ratings})