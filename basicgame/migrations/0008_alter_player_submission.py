# Generated by Django 4.2.1 on 2023-06-04 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basicgame', '0007_player_submission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='submission',
            field=models.CharField(max_length=1000),
        ),
    ]