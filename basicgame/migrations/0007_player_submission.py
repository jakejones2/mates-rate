# Generated by Django 4.2.1 on 2023-06-01 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basicgame', '0006_game_progress_alter_game_name_alter_player_game_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='submission',
            field=models.CharField(default='none', max_length=200),
            preserve_default=False,
        ),
    ]
