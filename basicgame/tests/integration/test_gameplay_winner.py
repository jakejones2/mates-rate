from basicgame.tests.integration.base import ThreePlayerTestGame
from selenium.webdriver.common.by import By


class TestGameplayWinner(ThreePlayerTestGame):
    """
    Class for testing the winner view during gameplay.
    """

    def test_correct_winner_shown(self):
        self.add_votes(
            '{"vote":{"name":"testuser112345678","voteData":{"category":"speed","characterScores":{"goat":"42","eagle":"95"}}}}',
            '{"vote":{"name":"testuser212345678","voteData":{"category":"speed","characterScores":{"goat":"50","eagle":"90"}}}}',
            '{"vote":{"name":"testuser312345678","voteData":{"category":"speed","characterScores":{"goat":"58","eagle":"85"}}}}',
        )
        self.add_submissions("_speed", "goat", "eagle")
        self.test_game.progress = 3
        self.test_game.save()
        self.start_three_player_game(wait_for_element="heading-smaller")
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading-smaller").text,
            "testuser3 wins!",
        )
        self.assertEqual(self.p2.selenium.find_element(By.ID, "score").text, "90")

    def test_draw_message(self):
        self.add_votes(
            '{"vote":{"name":"testuser112345678","voteData":{"category":"speed","characterScores":{"cat":"60","mouse":"50"}}}}',
            '{"vote":{"name":"testuser212345678","voteData":{"category":"speed","characterScores":{"cat":"50","mouse":"70"}}}}',
            '{"vote":{"name":"testuser312345678","voteData":{"category":"speed","characterScores":{"cat":"70","mouse":"60"}}}}',
        )
        self.add_submissions("_speed", "cat", "mouse")
        self.test_game.progress = 3
        self.test_game.save()
        self.start_three_player_game(wait_for_element="heading-smaller", time=10)
        self.p1.wait_for_element_text("heading-smaller")
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading-smaller").text,
            "Draw between testuser2 and testuser3",
        )
