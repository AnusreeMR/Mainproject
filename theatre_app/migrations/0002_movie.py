# Generated by Django 5.1.5 on 2025-01-22 09:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theatre_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movie_name', models.CharField(max_length=255)),
                ('movie_description', models.TextField()),
                ('movie_time_slot', models.CharField(max_length=100)),
                ('movie_genre', models.CharField(max_length=100)),
                ('movie_language', models.CharField(max_length=100)),
                ('movie_cast', models.TextField()),
                ('movie_crew', models.TextField()),
                ('movie_screen', models.CharField(max_length=100)),
                ('movie_trailer', models.URLField(blank=True, null=True)),
                ('movie_image', models.ImageField(blank=True, null=True, upload_to='movies/')),
                ('movie_certificate', models.CharField(max_length=10)),
                ('movie_duration', models.PositiveIntegerField()),
                ('movie_release_date', models.DateField()),
                ('movie_is_3d', models.BooleanField(default=False)),
                ('fk_theatre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movies', to='theatre_app.theatre_profile')),
            ],
        ),
    ]
