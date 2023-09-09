from basicgame.utils import calculate_winner
from basicgame.tests.unit.base import TripleTest, hash_database_async


class TestCalculateWinner(TripleTest):
    """
    Takes dictionary of scores and game_id.
    Should find the highest-scoring character, and check for a draw.
    Returns a dictionary of information containing the winner\drawers,
    draw status, the winning character and score if available, and category.
    Should have no side effects.
    """

    async def test_should_find_a_winner(self):
        await self.seed_db()
        scores = {"cat": 40, "dog": 60}
        output = await calculate_winner(scores, self.test_game.pk)
        expected = {
            "is_draw": False,
            "drawers_list": None,
            "name": "testuser2",
            "character": "dog",
            "category": "pets",
            "score": 60,
        }
        self.assertEqual(output, expected)

    async def test_should_find_a_draw(self):
        await self.seed_db()
        scores = {"cat": 50, "dog": 50}
        output = await calculate_winner(scores, self.test_game.pk)
        expected = {"is_draw": True, "drawers_list": ["testuser3", "testuser2"]}
        self.assertEqual(output, expected)

    async def test_should_not_alter_db(self):
        await self.seed_db()
        scores = {"cat": 50, "dog": 50}
        hash1 = await hash_database_async()
        await calculate_winner(scores, self.test_game.pk)
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)

    async def test_works_with_zero(self):
        await self.seed_db()
        scores = {"cat": 0, "dog": 60}
        output = await calculate_winner(scores, self.test_game.pk)
        expected = {
            "is_draw": False,
            "drawers_list": None,
            "name": "testuser2",
            "character": "dog",
            "category": "pets",
            "score": 60,
        }
        self.assertEqual(output, expected)

    async def test_works_with_zero_draw(self):
        await self.seed_db()
        scores = {"cat": 0, "dog": 0}
        output = await calculate_winner(scores, self.test_game.pk)
        expected = {"is_draw": True, "drawers_list": ["testuser3", "testuser2"]}
        self.assertEqual(output, expected)

    async def test_works_with_large_list(self):
        await self.seed_db()
        scores = {
            "cat": 70,
            "dog": 90,
            "hamster": 50,
            "rat": 20,
            "snake": 40,
            "pig": 0,
            "lizard": 40,
        }
        output = await calculate_winner(scores, self.test_game.pk)
        expected = {
            "is_draw": False,
            "drawers_list": None,
            "name": "testuser2",
            "character": "dog",
            "category": "pets",
            "score": 90,
        }
        self.assertEqual(output, expected)

    async def test_finds_triple_draw(self):
        await self.seed_db()
        await self.update_user1_submission("hamster")
        scores = {
            "cat": 90,
            "dog": 90,
            "hamster": 90,
            "rat": 20,
            "snake": 40,
            "pig": 0,
            "lizard": 40,
        }
        output = await calculate_winner(scores, self.test_game.pk)
        expected = {
            "is_draw": True,
            "drawers_list": ["testuser3", "testuser2", "testuser1"],
        }
        self.assertEqual(output, expected)

    async def test_does_not_mutate_scores(self):
        await self.seed_db()
        scores = {"cat": 50, "dog": 50}
        scores_copy = {"cat": 50, "dog": 50}
        await calculate_winner(scores, self.test_game.pk)
        self.assertEqual(scores, scores_copy)
