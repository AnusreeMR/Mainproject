from django.core.management.base import BaseCommand
from theatre_app.models import Seat, ShowTime, ShowtimeDate

class Command(BaseCommand):
    help = 'Generate seats only for new showtimes and dates without deleting existing ones'

    def handle(self, *args, **kwargs):
        showtimes = ShowTime.objects.all()  # Get all showtimes
        
        if not showtimes.exists():
            self.stdout.write(self.style.ERROR('No showtimes found. Please create showtimes first.'))
            return

        for showtime in showtimes:
            showtime_dates = ShowtimeDate.objects.filter(showtime=showtime)  # Get all dates for this showtime

            for show_date in showtime_dates:
                # Check if seats already exist for this showtime and date
                existing_seats = Seat.objects.filter(fk_showtime=showtime, fk_showtime__dates=show_date).exists()
                
                if existing_seats:
                    self.stdout.write(self.style.WARNING(f'Seats already exist for {showtime} on {show_date.date}. Skipping...'))
                    continue  # Skip to the next date if seats exist

                rows = 10  
                seats_per_row = 15  

                for row in range(1, rows + 1):
                    for seat in range(1, seats_per_row + 1):
                        unique_seat_number = f"{chr(64 + row)}{seat}-{showtime.id}-{show_date.id}"  # Unique format

                        Seat.objects.create(
                            fk_showtime=showtime,
                            row=chr(64 + row),  # Convert 1 -> A, 2 -> B, etc.
                            seat_number=unique_seat_number,  # Ensure uniqueness
                            is_booked=False
                        )

                self.stdout.write(self.style.SUCCESS(f'Successfully generated 100 seats for {showtime} on {show_date.date}'))
