from selenium.webdriver.common.by import By
from basicgame.tests.integration.base import (
    ThreePlayerTestGame,
    BoringThreePlayerTestGame,
)
from basicgame.models import Player


class TestGameplayVote(ThreePlayerTestGame):
    """
    Class for testing gameplay during the vote view for
    games with boring = false.
    """

    def setUp(self):
        super().setUp()
        self.add_submissions("_speed", "goat", "eagle")
        self.test_game.progress = 2
        self.test_game.save()

    def test_initial_category_header_correct(self):
        self.start_three_player_game()
        self.assertTrue(
            "speed" in self.p1.selenium.find_element(By.ID, "category").text
        )
        self.assertTrue(
            "goat" in self.p1.selenium.find_element(By.ID, "character").text
        )
        self.assertTrue(
            "speed" in self.p2.selenium.find_element(By.ID, "category").text
        )
        self.assertTrue(
            "goat" in self.p2.selenium.find_element(By.ID, "character").text
        )
        self.assertTrue(
            "speed" in self.p3.selenium.find_element(By.ID, "category").text
        )
        self.assertTrue(
            "goat" in self.p3.selenium.find_element(By.ID, "character").text
        )

    def test_characters_cycle_through_on_each_vote(self):
        self.start_three_player_game()
        self.assertTrue(
            "goat" in self.p1.selenium.find_element(By.ID, "character").text
        )
        self.p1.submit_game_text_and_wait("68", "character", "goat")
        self.assertTrue(
            "eagle" in self.p1.selenium.find_element(By.ID, "character").text
        )
        self.p1.submit_game_text("94")
        self.p1.wait_for_hidden("character")
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading-smaller").text,
            "Waiting for other players...",
        )

    def test_input_writes_correctly_to_db(self):
        self.start_three_player_game()
        self.p1.submit_game_text_and_wait("68", "character", "goat")
        self.p1.submit_game_text_and_wait("95", "character", "eagle")
        self.assertEqual(
            Player.objects.get(name="testuser112345678").votes,
            '{"vote":{"name":"testuser112345678","voteData":{"category":"speed","characterScores":{"goat":"68","eagle":"95"}}},"sender":"testuser112345678"}',
        )

    def test_three_inputs_leads_to_stage_2(self):
        self.start_three_player_game()
        self.p1.submit_game_text_and_wait("68", "character", "goat")
        self.p2.submit_game_text_and_wait("50", "character", "goat")
        self.p3.submit_game_text_and_wait("58", "character", "goat")
        self.submit_all(95, 90, 85)
        self.p3.wait_for_element_text("score")
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading-smaller").text,
            "testuser3 wins!",
        )
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "heading-smaller").text,
            "testuser3 wins!",
        )

        self.assertEqual(
            self.p3.selenium.find_element(By.ID, "heading-smaller").text,
            "testuser3 wins!",
        )

    def test_vote_validator(self):
        self.start_three_player_game()
        self.p1.submit_game_text(101)
        self.p1.wait_for_element_text("validator")
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "validator").text,
            "Enter a number between 0 and 100...",
        )
        self.assertTrue(
            self.p1.selenium.find_element(By.ID, "validator").is_displayed()
        )
        self.p1.wait_for_hidden("validator")
        self.p2.submit_game_text("abc")
        self.p2.wait_for_element_text("validator")
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "validator").text,
            "Enter a number between 0 and 100...",
        )
        self.assertTrue(
            self.p2.selenium.find_element(By.ID, "validator").is_displayed()
        )
        self.p3.submit_game_text("")
        self.p3.wait_for_element_text("validator")
        self.assertEqual(
            self.p3.selenium.find_element(By.ID, "validator").text,
            "Enter a number between 0 and 100...",
        )
        self.assertTrue(
            self.p3.selenium.find_element(By.ID, "validator").is_displayed()
        )

    def test_skip_round_goes_to_winner_view_if_enough_votes(self):
        self.start_three_player_game()
        self.p2.submit_game_text_and_wait("68", "character", "goat")
        self.p2.submit_game_text(72)
        self.p2.wait_for_element_text("heading-smaller")
        self.p1.selenium.find_element(By.ID, "force-next").click()
        self.p3.wait_for_element_text("score")
        self.assertEqual(
            self.p3.selenium.find_element(By.ID, "heading-smaller").text,
            "testuser3 wins!",
        )

    def test_skip_round_goes_to_skip_view_if_not_enough_votes(self):
        self.start_three_player_game()
        self.p2.submit_game_text_and_wait("68", "character", "goat")
        self.p1.selenium.find_element(By.ID, "force-next").click()
        self.p3.wait_for_element_text("heading-smaller")
        self.assertEqual(
            self.p3.selenium.find_element(By.ID, "heading-smaller").text,
            "Round skipped by host...",
        )


class TestBoringGameplayVote(BoringThreePlayerTestGame):
    """
    Class for testing gameplay during the vote view for
    games with boring = true.
    """

    def test_boring_mode_votes_added_correctly(self):
        self.start_three_player_game()
        self.submit_all("speed", None, None)
        self.p1.wait_for_element_text("heading-smaller")
        self.submit_all(None, "cat", "dog")
        self.p3.wait_for_element_text("heading")
        self.assertEqual(self.p2.selenium.find_element(By.ID, "category").text, "speed")
        self.assertEqual(self.p2.selenium.find_element(By.ID, "character").text, "cat")
        self.submit_all(None, "80", None)
        self.p2.wait_for_text_change("character", "cat")
        self.assertEqual(self.p2.selenium.find_element(By.ID, "character").text, "dog")
