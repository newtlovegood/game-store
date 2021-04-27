# Generated by Django 3.2 on 2021-04-27 07:01

from django.db import migrations, models


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
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('price', models.FloatField()),
                ('description', models.TextField(default='')),
                ('genre', models.ManyToManyField(blank=True, to='games.Genre')),
            ],
        ),
    ]
