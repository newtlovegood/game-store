from django.db import migrations

genres = [
    'Strategy',
    'RPG',
    'Sports',
    'Races-Rally',
    'Races-Arcade',
    'Races-Formula',
    'Races-Off-Road',
    'Action-FPS',
    'Action-TPS',
    'Action-Misc',
    'Adventure',
    'Puzzle & Skills',
    'Other',
]


def populate_genres(apps, schema):

    Genre = apps.get_model('games', 'Genre')
    for genre in genres:
        Genre.objects.create(name=genre)


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_genres),
    ]
