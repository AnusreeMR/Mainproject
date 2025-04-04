from django.urls import path
from .views import *

urlpatterns = [
    
    # Common Routes
    path('',landing,name="landing"),
    
    path('user_login',user_login,name="user_login"),
    path('logout',user_logout, name='user_logout'),
    path('forgot_password/',forgot_password, name='forgot_password'),
    path('reset_password/<uidb64>/<token>/',reset_password, name='reset_password'),
    
    # Admin Routes   
    
    path('admin-dashboard',admin_dashboard, name='admin_dashboard'),
    path('user-list1',user_list1,name="user_list1"),
    path('theatre-list',theatre_list,name="theatre_list"),
    path('user-delete/<int:id>',user_delete,name="user_delete"),
    
    # Theatre Operator Routes
    
    path('theatre-operator-register',theatre_operator_register, name='theatre_operator_register'),
    path('theatre-operator-dashboard',theatre_operator_dashboard, name='theatre_operator_dashboard'),
    path('theatre_add_movies',theatre_add_movies,name="theatre_add_movies"),
    path('theatre_show_movies',theatre_show_movies,name="theatre_show_movies"),
    path('movie/edit/<int:id>/', theatre_edit_movies, name='theatre_edit_movies'),
    path('movie/delete/<int:id>/', theatre_delete_movies, name='theatre_delete_movies'),
    path('theatre/shows/', theatre_shows, name='theatre_shows'),
    path('get-showtime-dates/<int:showtime_id>/',get_showtime_dates, name='get_showtime_dates'),
    path("remove-showtime-date/<int:showtime_id>/<int:date_id>/", remove_showtime_date, name="remove_showtime_date"),
    
   


    # User Routes   book_seat' showtime.id

    path('user_register',user_register,name="user_register"),
    path('user-dashboard',user_dashboard, name='user_dashboard'),
    path('theatre/<int:theatre_id>/', theatre_movies, name='theatre_movies'),

    path('theatre_layout/',the_gg, name='theatre_layout'),





    path('theatre-admin/bookings-details/', theatre_admin_bookings_details, name='theatre_admin_bookings_details'),
    path('theatre-admin/theatre_x/', theatre_x, name='theatre_x'),

    path('movies_list_x/', movies_list_x, name='movies_list_x'),
    path('movies_list_x/<int:movie_id>/', movie_detail_x, name='movie_detail_x'),

    path('submit_rating/', submit_rating, name='submit_rating'),
    path('submit_comment/', submit_comment, name='submit_comment'),



    path('delete-comment/<int:rating_id>/', delete_comment, name='delete_comment'),
    path('delete-rating/<int:rating_id>/', delete_rating, name='delete_rating'),


    ##################  Complaints ###########################

    path('complaints/', user_complaints, name='user_complaints'),
    path('admin-complaints/', admin_complaints, name='admin_complaints'),
    path('theatre_to_admin_complaints/', theatre_to_admin_complaints, name='theatre_to_admin_complaints'),
    path('list_theatre_to_admin_complaints_list/', list_theatre_to_admin_complaints_list, name='list_theatre_to_admin_complaints_list'),


#########################################################

    path('theatre-complaints/', user_theatre_complaints, name='user_theatre_complaints'),
    path('list_user_complaints_to_theatre/', list_user_complaints_to_theatre, name='list_user_complaints_to_theatre'),



    path('book-seat/', book_seat, name='book_seat'),
    path('seat-booking/<int:showtime_id>/', seat_booking, name='seat_booking'),

    path('booking-history/',booking_history, name='booking_history'),
    path("cancel-booking/<int:booking_id>/", cancel_booking, name="cancel_booking"),

    path('theatre-admin/bookings/', theatre_admin_bookings, name='theatre_admin_bookings'),
    path('theatre-admin/bookings/approve/<int:booking_id>/', approve_cancellation, name='approve_cancellation'),

    ###############################################################################

    path('theatres/', user_theatre_list, name='user_theatre_list'),
    path('submit-theatre-rating/', submit_theatre_rating, name='submit_theatre_rating'),


    path('admin_view_theatre_reating/', admin_view_theatre_rating, name='admin_view_theatre_reating'),
    path('admin_movie-ratings/', admin_view_movie_rating, name='admin_view_movie_rating'),


    path('generate-seats/', generate_seats, name='generate_seats'),
    
]



