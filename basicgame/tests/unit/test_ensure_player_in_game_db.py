from basicgame.utils import ensure_player_in_game_db
from basicgame.tests.unit.base import (
    SingleTest,
    hash_database_async,
    get_players,
)


class TestEnsurePLayerInGameDb(SingleTest):
    """
    Function should check if given player is in
    the game database. If not, the player is added to this database.
    """

    async def test_function_adds_to_db(self):
        self.assertFalse("testuser212345678" in await get_players(self.test_game.name))
        await ensure_player_in_game_db("testuser212345678", self.test_game.pk)
        self.assertTrue("testuser212345678" in await get_players("testgame"))

    async def test_function_does_nothing_if_player_in_game(self):
        # see base.py
        hash1 = await hash_database_async()
        await ensure_player_in_game_db("testuser112345678", self.test_game.pk)
        self.assertTrue("testuser112345678" in await get_players(self.test_game.name))
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)
