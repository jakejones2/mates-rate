from django.db import models
from django.core.validators import RegexValidator


class Game(models.Model):
    """
    A new record is created in the Game table for each game played.
    Cycles: number of rounds to be played per player. E.g. three cycles with
    three players is 9 rounds (and 47/54 views).
    Boring: Boolean representing whether the game should be played in 'boring' mode.
    """

    name = models.CharField(max_length=30)
    cycles = models.PositiveSmallIntegerField()
    boring = models.BooleanField()
    host = models.CharField(max_length=50)
    progress = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Player(models.Model):
    """
    A new record is created in the Player table for each player who joins the game.
    The game_id field is a foreign key to the Game table.

    Points: the score of each player, highest wins.

    Submission: categories and characters are stored in this field. Categories are
                autmatically prefixed with an underscore (e.g. '_truthfullness')

    Votes: scores for combinations of characters and categories are store here.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[
            RegexValidator(
                "^[A-Za-z0-9_-]+$", "Letters, numbers, '_' and '-' only please"
            )
        ],
    )
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    points = models.PositiveSmallIntegerField()
    submission = models.CharField(max_length=100, null=True)
    votes = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return self.name
