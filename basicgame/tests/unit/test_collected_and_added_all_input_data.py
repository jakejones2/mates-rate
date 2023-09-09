from basicgame.tests.unit.base import TripleTest, hash_database_async
from basicgame.utils import collected_and_added_all_input_data


class TestCollectedAndAddedAllInputData(TripleTest):
    """
    Tests for util function collected_and_added_all_input_data.
    This function should collect submissions and votes, add them to the database,
    and return true if all players in the game have contributed.
    """

    async def test_adds_one_player_submission_to_db(self):
        await collected_and_added_all_input_data(
            "testuser112345678", "submission", "data1", self.test_game.id
        )
        self.assertEqual(await self.get_submission("testuser112345678"), "data1")

    async def test_does_not_do_anything_if_called_twice_with_same_data(self):
        await collected_and_added_all_input_data(
            "testuser112345678", "submission", "data1", self.test_game.id
        )
        await collected_and_added_all_input_data(
            "testuser112345678", "submission", "data1", self.test_game.id
        )
        self.assertEqual(await self.get_submission("testuser112345678"), "data1")

    async def test_asterisks_added_upon_duplication(self):
        await collected_and_added_all_input_data(
            "testuser112345678", "submission", "data1", self.test_game.id
        )
        await collected_and_added_all_input_data(
            "testuser212345678", "submission", "data1", self.test_game.id
        )
        self.assertEqual(await self.get_submission("testuser212345678"), "data1*")

    async def test_returns_true_if_all_players_added_data(self):
        await collected_and_added_all_input_data(
            "testuser112345678", "submission", "data1", self.test_game.id
        )
        await collected_and_added_all_input_data(
            "testuser212345678", "submission", "data1", self.test_game.id
        )
        output = await collected_and_added_all_input_data(
            "testuser312345678", "submission", "data1", self.test_game.id
        )
        self.assertEqual(await self.get_submission("testuser312345678"), "data1**")
        self.assertTrue(output)

    async def test_can_update_a_submission(self):
        await collected_and_added_all_input_data(
            "testuser212345678", "submission", "data1", self.test_game.id
        )
        await collected_and_added_all_input_data(
            "testuser212345678", "submission", "data2", self.test_game.id
        )
        self.assertEqual(await self.get_submission("testuser212345678"), "data2")

    async def test_should_only_modify_given_field_in_db(self):
        hash1 = await hash_database_async(discounted=["submission"])
        await collected_and_added_all_input_data(
            "testuser312345678", "submission", "data1", self.test_game.id
        )
        hash2 = await hash_database_async(discounted=["submission"])
        self.assertEqual(hash1, hash2)
