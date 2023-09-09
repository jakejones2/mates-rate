from basicgame.utils import create_results_html_table
from basicgame.tests.unit.base import hash_database_async
from django.test import TransactionTestCase


class TestCreateResultsHtmlTable(TransactionTestCase):
    """
    Should take a dictionary of scores and a category.
    Orders scores in descending order and returns a string representing
    an HTML table. Saves extra js on the front end.
    Function should have no side effects.
    """

    async def test_returns_correct_sorted_html_table(self):
        scores = {"cat": 40, "dog": 60}
        output = await create_results_html_table(scores, "pets")
        self.assertEqual(
            output,
            "<tr><th>character</th><th>pets</th></tr><tr><td>dog</td><td>60</td></tr><tr><td>cat</td><td>40</td></tr>",
        )

    async def test_does_not_alter_database(self):
        hash1 = await hash_database_async()
        scores = {"cat": 40, "dog": 60}
        await create_results_html_table(scores, "pets")
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)

    async def test_does_not_mutate_scores(self):
        scores = {"cat": 40, "dog": 60}
        scores_copy = {"cat": 40, "dog": 60}
        await create_results_html_table(scores, "pets")
        self.assertEqual(scores, scores_copy)
