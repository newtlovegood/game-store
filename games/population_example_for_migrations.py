from django.db import migrations

genres = [
    'Strategy',
    'RPG',
    'Sports',
    'Races_Rally',
    'Races_Arcade',
    'Races_Formula',
    'Races_Off-Road',
    'Action_FPS',
    'Action_TPS',
    'Action_Misc',
    'Adventure',
    'Puzzle_Skills',
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
