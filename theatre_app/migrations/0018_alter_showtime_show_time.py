# Generated by Django 5.1.6 on 2025-04-03 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theatre_app', '0017_theatre_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='showtime',
            name='show_time',
            field=models.TimeField(max_length=10),
        ),
    ]
