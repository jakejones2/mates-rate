from basicgame.utils import generate_progress_string
from basicgame.tests.unit.base import TripleTest, hash_database_async
from channels.db import database_sync_to_async  # type: ignore


class TestGetPlayerFromCookie(TripleTest):
    """
    Function should take game_id and calculate the
    current round and total rounds. Return a string
    representing this information.
    Should have no side effects.
    """

    async def test_returns_correct_string_in_lobby(self):
        output = await generate_progress_string(self.test_game.pk)
        self.assertEqual(output, "Round 0 of 12")

    async def test_returns_correct_string_in_submission(self):
        await self.set_game_progress(1)
        output = await generate_progress_string(self.test_game.pk)
        self.assertEqual(output, "Round 1 of 12")

    async def test_returns_correct_string_in_higher_round(self):
        await self.set_game_progress(39)
        output = await generate_progress_string(self.test_game.pk)
        self.assertEqual(output, "Round 8 of 12")

    async def test_works_in_final_round(self):
        await self.set_game_progress(60)
        output = await generate_progress_string(self.test_game.pk)
        self.assertEqual(output, "Round 12 of 12")

    async def test_works_in_final_view_of_round(self):
        await self.set_game_progress(5)
        output = await generate_progress_string(self.test_game.pk)
        self.assertEqual(output, "Round 1 of 12")

    async def test_does_not_mutate_db(self):
        await self.set_game_progress(39)
        hash1 = await hash_database_async()
        await generate_progress_string(self.test_game.pk)
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)

    @database_sync_to_async
    def make_boring(self):
        self.test_game.boring = True
        self.test_game.save()

    async def test_works_in_boring_mode(self):
        await self.make_boring()
        await self.set_game_progress(0)
        output = await generate_progress_string(self.test_game.pk)
        self.assertEqual(output, "Round 0 of 12")

    async def test_works_in_boring_mode_submission(self):
        await self.make_boring()
        await self.set_game_progress(1)
        output = await generate_progress_string(self.test_game.pk)
        self.assertEqual(output, "Round 1 of 12")

    async def test_works_in_boring_mode_later_rounds(self):
        await self.make_boring()
        await self.set_game_progress(13)
        output = await generate_progress_string(self.test_game.pk)
        self.assertEqual(output, "Round 3 of 12")

    async def test_works_in_boring_mode_where_would_fail_in_normal(self):
        await self.make_boring()
        await self.set_game_progress(24)
        output = await generate_progress_string(self.test_game.pk)
        self.assertEqual(output, "Round 4 of 12")
