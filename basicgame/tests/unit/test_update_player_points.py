from basicgame.utils import update_player_points
from basicgame.tests.unit.base import TripleTest, hash_database_async
from basicgame.models import Player, Game
from channels.db import database_sync_to_async  # type: ignore


class TestUpdatePlayerPoints(TripleTest):
    """
    Should take scores dictionary and game_id.
    Creates an ordered list of characters and scores from highest to lowest,
    and iterates through this list. On each charater, the function retreives
    the matching player from the db, and increases their points as determined
    by the generator. If there are two or more matching scores in a row
    (i.e, a draw), then these subsequent players recieve the same amount of
    points as the first player and the generator is not called.
    """

    async def test_updates_scores_correctly_upon_winner_three_players(self):
        await self.seed_db()
        scores = {"cat": 40, "dog": 60}
        await update_player_points(scores, self.test_game.pk)
        self.assertEqual(await self.get_points(self.user1.name), 0)
        self.assertEqual(await self.get_points(self.user2.name), 1)
        self.assertEqual(await self.get_points(self.user3.name), 0)

    async def test_allocates_equal_points_to_drawers(self):
        await self.seed_db()
        scores = {"cat": 50, "dog": 50}
        await update_player_points(scores, self.test_game.pk)
        self.assertEqual(await self.get_points(self.user1.name), 0)
        self.assertEqual(await self.get_points(self.user2.name), 1)
        self.assertEqual(await self.get_points(self.user3.name), 1)

    async def test_does_not_modify_db_other_than_points(self):
        await self.seed_db()
        scores = {"cat": 50, "dog": 50}
        hash1 = await hash_database_async()
        hash2 = await hash_database_async(discounted=["points"])
        await update_player_points(scores, self.test_game.pk)
        hash3 = await hash_database_async()
        hash4 = await hash_database_async(discounted=["points"])
        self.assertNotEqual(hash1, hash3)
        self.assertEqual(hash2, hash4)

    async def test_works_on_large_group_with_internal_draw(self):
        await self.seed_large_db()
        scores = {
            "cat": 70,
            "dog": 90,
            "hamster": 50,
            "rat": 20,
            "snake": 40,
            "pig": 0,
            "lizard": 40,
        }
        await update_player_points(scores, self.large_game.pk)
        self.assertEqual(await self.get_points(self.newuser1), 0)
        self.assertEqual(await self.get_points(self.newuser2), 5)
        self.assertEqual(await self.get_points(self.newuser3), 3)
        self.assertEqual(await self.get_points(self.newuser4), 2)
        self.assertEqual(await self.get_points(self.newuser5), 0)
        self.assertEqual(await self.get_points(self.newuser6), 1)
        self.assertEqual(await self.get_points(self.newuser7), 0)
        self.assertEqual(await self.get_points(self.newuser8), 1)

    async def test_does_not_mutate_scores(self):
        await self.seed_db()
        scores = {"cat": 40, "dog": 60}
        scores_copy = {"cat": 40, "dog": 60}
        await update_player_points(scores, self.test_game.pk)
        self.assertEqual(scores, scores_copy)

    @database_sync_to_async
    def seed_large_db(self):
        self.large_game = Game.objects.create(
            name="testgamelarge",
            cycles=4,
            boring=False,
            host="newuser112345678",
            progress=1,
        )
        self.newuser1 = Player.objects.create(
            name="newuser112345678",
            game_id=self.large_game,
            points=0,
            submission="_pets",
            votes=None,
        )
        self.newuser2 = Player.objects.create(
            name="newuser212345678",
            game_id=self.large_game,
            points=0,
            submission="dog",
            votes=None,
        )
        self.newuser3 = Player.objects.create(
            name="newuser312345678",
            game_id=self.large_game,
            points=0,
            submission="cat",
            votes=None,
        )
        self.newuser4 = Player.objects.create(
            name="newuser412345678",
            game_id=self.large_game,
            points=0,
            submission="hamster",
            votes=None,
        )
        self.newuser5 = Player.objects.create(
            name="newuser512345678",
            game_id=self.large_game,
            points=0,
            submission="rat",
            votes=None,
        )
        self.newuser6 = Player.objects.create(
            name="newuser612345678",
            game_id=self.large_game,
            points=0,
            submission="snake",
            votes=None,
        )
        self.newuser7 = Player.objects.create(
            name="newuser712345678",
            game_id=self.large_game,
            points=0,
            submission="pig",
            votes=None,
        )
        self.newuser8 = Player.objects.create(
            name="newuser812345678",
            game_id=self.large_game,
            points=0,
            submission="lizard",
            votes=None,
        )
