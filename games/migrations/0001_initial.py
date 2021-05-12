# Generated by Django 3.2 on 2021-05-12 06:08

import django.core.validators
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Strategy', 'Strategy'), ('RPG', 'RPG'), ('Sports', 'Sports'), ('Races/Rally', 'Races/Rally'), ('Races/Arcade', 'Races/Arcade'), ('Races/Formula', 'Races/Formula'), ('Races/Off-Road', 'Races/Off-Road'), ('Action/FPS', 'Action/FPS'), ('Action/TPS', 'Action/TPS'), ('Action/Misc', 'Action/Misc'), ('Adventure', 'Adventure'), ('Puzzle/Skills', 'Puzzle/Skills'), ('Other', 'Other')], max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=300)),
                ('price', models.FloatField()),
                ('description', models.TextField(default='')),
                ('image', models.ImageField(default='images/games/default.jpg', upload_to='images/games')),
                ('in_stock', models.BooleanField(default=False)),
                ('quantity_available', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(7858772994)])),
                ('genre', models.ManyToManyField(blank=True, to='games.Genre')),
            ],
            options={
                'ordering': ['-in_stock'],
            },
        ),
    ]
