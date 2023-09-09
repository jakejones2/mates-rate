from django.test import TestCase, TransactionTestCase
from basicgame.models import Player, Game
from channels.db import database_sync_to_async  # type: ignore
import hashlib
import json


def hash_database(discounted=[]):
    data_list = []
    for game in Game.objects.all():
        data_list.append(["boring", game.boring])
        data_list.append(["game_name", game.name])
        data_list.append(["cycles", game.cycles])
        data_list.append(["host", game.host])
        data_list.append(["progress", game.progress])
    for player in Player.objects.all():
        data_list.append(["points", player.points])
        data_list.append(["player_name", player.name])
        data_list.append(["submission", player.submission])
        data_list.append(["votes", player.votes])
    for field in discounted:
        data_list = [entry for entry in data_list if not entry[0] == field]
    bytes = json.dumps(data_list).encode("utf-8")
    return hashlib.sha256(bytes).hexdigest()


@database_sync_to_async
def hash_database_async(discounted=[]):
    return hash_database(discounted)


@database_sync_to_async
def get_players(game_name):
    game_id: int = Game.objects.get(name=game_name).pk
    player_query_set = Player.objects.filter(game_id=game_id)
    return [player.name for player in player_query_set]


class TripleTest(TransactionTestCase):
    """
    Class for testing functions that require at least
    three players in the Game database.
    """

    def setUp(self):
        super().setUp()
        self.test_game = Game.objects.create(
            name="testgame",
            cycles=4,
            boring=False,
            host="testuser112345678",
            progress=0,
        )
        self.user1 = Player.objects.create(
            name="testuser112345678",
            game_id=self.test_game,
            points=0,
            submission=None,
            votes=None,
        )
        self.user2 = Player.objects.create(
            name="testuser212345678",
            game_id=self.test_game,
            points=0,
            submission=None,
            votes=None,
        )
        self.user3 = Player.objects.create(
            name="testuser312345678",
            game_id=self.test_game,
            points=0,
            submission=None,
            votes=None,
        )

    @database_sync_to_async
    def update_submissions(self, sub1, sub2, sub3):
        self.user1.submission = sub1
        self.user1.save()
        self.user2.submission = sub2
        self.user2.save()
        self.user3.submission = sub3
        self.user3.save()

    @database_sync_to_async
    def update_votes(self, vote1, vote2, vote3):
        self.user1.votes = vote1
        self.user1.save()
        self.user2.votes = vote2
        self.user2.save()
        self.user3.votes = vote3
        self.user3.save()

    @database_sync_to_async
    def update_points(self, p1, p2, p3):
        self.user1.points = p1
        self.user1.save()
        self.user2.points = p2
        self.user2.save()
        self.user3.points = p3
        self.user3.save()

    @database_sync_to_async
    def update_user1_vote(self, value):
        self.user1.votes = value
        self.user1.save()

    @database_sync_to_async
    def update_user1_submission(self, value):
        self.user1.submission = value
        self.user1.save()

    async def seed_db(self):
        await self.update_submissions("_pets", "dog", "cat")
        await self.update_votes(
            '{"vote":{"name":"testuser112345678","voteData":{"category":"pets","characterScores":{"dog":"80","cat":"20"}}}}',
            '{"vote":{"name":"testuser212345678","voteData":{"category":"pets","characterScores":{"dog":"60","cat":"40"}}}}',
            '{"vote":{"name":"testuser312345678","voteData":{"category":"pets","characterScores":{"dog":"40","cat":"60"}}}}',
        )

    @database_sync_to_async
    def seed_new_game(self):
        self.new_game = Game.objects.create(
            name="testgame", cycles=4, boring=False, host="testuser4", progress=1
        )
        self.new_player = Player.objects.create(
            name="testuser4",
            game_id=self.new_game,
            points=0,
            submission="dogs",
            votes='{"vote":{"name":"testuser112345678","voteData":{"category":"pets","characterScores":{"dog":"80","cat":"20"}}}}',
        )

    @database_sync_to_async
    def get_submission(self, player_name):
        player = Player.objects.get(name=player_name)
        return player.submission

    @database_sync_to_async
    def get_points(self, player_name):
        player = Player.objects.get(name=player_name)
        return player.points

    @database_sync_to_async
    def set_game_progress(self, progress):
        self.test_game.progress = progress
        self.test_game.save()

    @database_sync_to_async
    def get_game_progress(self):
        game = Game.objects.get(id=self.test_game.pk)
        return game.progress


class SingleTest(TransactionTestCase):
    """
    Class for testing functions that conern individual
    players only and their database record.
    """

    def setUp(self):
        super().setUp()
        self.test_game = Game.objects.create(
            name="testgame",
            cycles=4,
            boring=False,
            host="testuser112345678",
            progress=0,
        )
        self.user = Player.objects.create(
            name="testuser112345678",
            game_id=self.test_game,
            points=0,
            submission=None,
            votes=None,
        )
