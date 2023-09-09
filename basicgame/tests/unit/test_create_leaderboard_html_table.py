from basicgame.utils import create_leaderboard_html_table
from basicgame.tests.unit.base import hash_database_async, TripleTest


class TestCreateLeaderboardHtmlTable(TripleTest):
    """
    Takes game_id. Creates sorted list of players based
    on their points as retrieved from the database.
    Should have no side effects.
    """

    async def test_returns_correct_table_upon_win(self):
        await self.update_points(1, 2, 3)
        output = await create_leaderboard_html_table(self.test_game.pk)
        self.assertEqual(
            output,
            "<tr><th>player</th><th>points</th></tr><tr><td>testuser3</td><td>3</td></tr><tr><td>testuser2</td><td>2</td></tr><tr><td>testuser1</td><td>1</td></tr>",
        )

    async def test_sorts_alphabetically_upon_tie(self):
        await self.update_points(2, 2, 3)
        output = await create_leaderboard_html_table(self.test_game.pk)
        self.assertEqual(
            output,
            "<tr><th>player</th><th>points</th></tr><tr><td>testuser3</td><td>3</td></tr><tr><td>testuser1</td><td>2</td></tr><tr><td>testuser2</td><td>2</td></tr>",
        )

    async def test_does_not_alter_database(self):
        await self.update_points(1, 2, 3)
        hash1 = await hash_database_async()
        await create_leaderboard_html_table(self.test_game.pk)
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)
