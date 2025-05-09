# Generated by Django 5.1.5 on 2025-02-25 10:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theatre_app', '0008_remove_showtime_date_showtimedate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_type', models.CharField(choices=[('direct', 'Direct Booking'), ('flexi', 'Flexi Booking')], max_length=10)),
                ('payment_method', models.CharField(choices=[('gpay', 'Google Pay'), ('phonepe', 'PhonePe'), ('paytm', 'Paytm')], max_length=10)),
                ('booking_date', models.DateTimeField(auto_now_add=True)),
                ('is_cancelled', models.BooleanField(default=False)),
                ('fk_seat', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='booking', to='theatre_app.seat')),
                ('fk_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
