# Generated by Django 5.1.6 on 2025-03-28 17:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theatre_app', '0016_theatrecomplaint'),
    ]

    operations = [
        migrations.CreateModel(
            name='Theatre_Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('theatre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tratings', to='theatre_app.theatre_profile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
