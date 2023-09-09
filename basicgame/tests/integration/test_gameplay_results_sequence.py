from basicgame.tests.integration.base import ThreePlayerTestGame
from selenium.webdriver.common.by import By


class TestGameplayResultsSequence(ThreePlayerTestGame):
    """
    Class for testing the automatic flow of views within gameplay.
    """

    def setUp(self):
        super().setUp()
        self.add_submissions("_screaming", "goat", "eagle")
        self.test_game.progress = 2
        self.test_game.save()
        self.start_three_player_game()
        self.p3.wait_for_element_text("character")
        self.submit_all(95, 90, 85)
        self.p3.wait_for_text_change("character", "goat")
        self.submit_all(60, 70, 50)
        self.p3.wait_for_element_text("heading-smaller")
        self.p3.wait_for_element_text("score")

    def test_winner_results_leaderboard_loop_sequence(self):
        self.assertTrue(self.p1.selenium.find_element(By.ID, "score").text)
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading-smaller").text,
            "testuser2 wins!",
        )
        self.p1.wait_for_element_text("heading", 10)
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading").text, "Results"
        )
        self.p1.wait_for_element_text("heading-smaller", 10)
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading-smaller").text, "Leaderboard"
        )
        self.p1.wait_for_element_text("heading", 10)
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading").text, "Enter a character:"
        )

    def test_skip_round_during_results_sequence_goes_to_next_round(self):
        self.assertTrue(self.p1.selenium.find_element(By.ID, "score").text)
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading-smaller").text,
            "testuser2 wins!",
        )
        self.p1.wait_for_element_text("heading", 10)
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading").text, "Results"
        )
        self.p1.selenium.find_element(By.ID, "force-next").click()
        self.p3.wait_for_element_text("heading-smaller")
        self.p3.wait_for_hidden("heading", invert=True)
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "heading").text, "Enter a category:"
        )
