from selenium.webdriver.common.by import By
from basicgame.tests.integration.base import (
    ThreePlayerTestGame,
    BoringThreePlayerTestGame,
)


class TestGameplaySubmission(ThreePlayerTestGame):
    """
    Class for testing gameplay during the submission view for
    games with boring = false.
    """

    def setUp(self):
        super().setUp()
        self.start_three_player_game()

    def all_wait_for_heading_smaller(self):
        self.p1.wait_for_element_text("heading-smaller")
        self.p2.wait_for_element_text("heading-smaller")
        self.p3.wait_for_element_text("heading-smaller")

    def test_two_character_prompts_and_one_category(self):
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading").text, "Enter a category:"
        )
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "heading").text, "Enter a character:"
        )
        self.assertEqual(
            self.p3.selenium.find_element(By.ID, "heading").text, "Enter a character:"
        )

    # selenium_1 is host
    def test_only_host_can_see_skip_round_button(self):
        self.assertTrue(
            self.p1.selenium.find_element(By.ID, "force-next").is_displayed()
        )
        self.assertFalse(
            self.p2.selenium.find_element(By.ID, "force-next").is_displayed()
        )
        self.assertFalse(
            self.p3.selenium.find_element(By.ID, "force-next").is_displayed()
        )

    def test_one_sending_data_does_not_advance_game(self):
        self.submit_all("speed", None, None)
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading-smaller").text,
            "Waiting for other players...",
        )
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "heading").text, "Enter a character:"
        )
        self.assertEqual(
            self.p3.selenium.find_element(By.ID, "heading").text, "Enter a character:"
        )

    def test_two_sending_data_does_not_advance_game(self):
        self.submit_all("speed", "goat", None)
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading-smaller").text,
            "Waiting for other players...",
        )
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "heading-smaller").text,
            "Waiting for other players...",
        )
        self.assertEqual(
            self.p3.selenium.find_element(By.ID, "heading").text, "Enter a character:"
        )

    def test_three_sending_data_does_advance_game(self):
        self.submit_all("speed", "goat", "eagle")
        self.p3.wait_for_element_text("category")
        self.assertEqual(self.p1.selenium.find_element(By.ID, "heading").text, "Vote!")
        self.assertEqual(self.p2.selenium.find_element(By.ID, "heading").text, "Vote!")
        self.assertEqual(self.p3.selenium.find_element(By.ID, "heading").text, "Vote!")

    def test_force_next_advances_game_for_all(self):
        self.p1.selenium.find_element(By.ID, "force-next").click()
        self.all_wait_for_heading_smaller()
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading-smaller").text,
            "Round skipped by host...",
        )
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "heading-smaller").text,
            "Round skipped by host...",
        )
        self.assertEqual(
            self.p3.selenium.find_element(By.ID, "heading-smaller").text,
            "Round skipped by host...",
        )

    def test_force_next_advances_to_next_round_after_delay(self):
        self.p1.selenium.find_element(By.ID, "force-next").click()
        self.all_wait_for_heading_smaller()
        self.p1.wait_for_hidden("heading-smaller", time=15)
        self.p2.wait_for_hidden("heading-smaller", time=15)
        self.p3.wait_for_hidden("heading-smaller", time=15)
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading").text, "Enter a character:"
        )
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "heading").text, "Enter a category:"
        )
        self.assertEqual(
            self.p3.selenium.find_element(By.ID, "heading").text, "Enter a character:"
        )
        footer_1 = self.p1.selenium.find_element(By.ID, "game-name-footer").text
        self.p1.wait_for_text_change("game-name-footer", footer_1, 8)
        footer_2 = self.p1.selenium.find_element(By.ID, "game-name-footer").text
        self.p1.wait_for_text_change("game-name-footer", footer_2, 8)
        footer_3 = self.p1.selenium.find_element(By.ID, "game-name-footer").text
        self.assertTrue(footer_2 == "Round 2 of 6" or footer_3 == "Round 2 of 6")

    def test_force_next_advances_game_with_partial_data(self):
        self.p1.add_submission("_speed")
        self.p2.add_submission("goat")
        self.p1.selenium.find_element(By.ID, "force-next").click()
        self.p1.wait_for_text_change("heading", "Enter a category:")
        self.p2.wait_for_text_change("heading", "Enter a character:")
        self.p3.wait_for_text_change("heading", "Enter a character:")
        self.assertEqual(self.p1.selenium.find_element(By.ID, "heading").text, "Vote!")
        self.assertEqual(self.p2.selenium.find_element(By.ID, "heading").text, "Vote!")
        self.assertEqual(self.p3.selenium.find_element(By.ID, "heading").text, "Vote!")

    def test_input_validators(self):
        self.p1.selenium.find_element(By.ID, "game-submit").click()
        self.p2.selenium.find_element(By.ID, "game-submit").click()
        self.p1.wait_for_element_text("validator")
        self.assertTrue(
            self.p1.selenium.find_element(By.ID, "validator").is_displayed()
        )
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "validator").text,
            "Enter a longer category...",
        )
        self.assertTrue(
            self.p2.selenium.find_element(By.ID, "validator").is_displayed()
        )
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "validator").text,
            "Enter a longer character...",
        )
        self.assertTrue(
            self.p2.selenium.find_element(By.ID, "validator").is_displayed()
        )

    def test_duplicate_characters_have_asterisks(self):
        self.submit_all("_speed", "cat", "cat")
        self.p3.wait_for_element_text("category")
        self.assertEqual(self.p1.selenium.find_element(By.ID, "character").text, "cat")
        self.p1.submit_game_text_and_wait("70", "character", "cat")
        self.assertEqual(self.p1.selenium.find_element(By.ID, "character").text, "cat*")


class TestBoringGameplaySubmission(BoringThreePlayerTestGame):
    """
    Class for testing gameplay during the submission view for
    games with boring = true.
    """

    def setUp(self):
        super().setUp()
        self.start_three_player_game()

    def test_one_category_prompt_and_two_wait_messages(self):
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading").text, "Enter a category:"
        )
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "heading-smaller").text,
            "Waiting for\ntestuser1\nto offer a category...",
        )
        self.assertEqual(
            self.p3.selenium.find_element(By.ID, "heading-smaller").text,
            "Waiting for\ntestuser1\nto offer a category...",
        )
        self.assertTrue(
            self.p2.selenium.find_element(By.ID, "heading-smaller").is_displayed()
        )

    def test_entering_category_advances_game(self):
        self.submit_all("speed", None, None)
        self.p1.wait_for_element_text("heading-smaller")
        self.p1.wait_for_text_change("heading-smaller", "Waiting for server...")
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "heading-smaller").text,
            "Waiting for characters...",
        )
        self.assertTrue(
            self.p2.selenium.find_element(By.ID, "boring-category").is_displayed()
        )
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "boring-category").text, "speed"
        )
        self.assertTrue(self.p2.selenium.find_element(By.ID, "heading").is_displayed())
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "heading").text,
            "Enter a character:",
        )
        self.assertTrue(
            self.p3.selenium.find_element(By.ID, "boring-category").is_displayed()
        )
        self.assertEqual(
            self.p3.selenium.find_element(By.ID, "boring-category").text, "speed"
        )
        self.assertTrue(self.p3.selenium.find_element(By.ID, "heading").is_displayed())
        self.assertEqual(
            self.p3.selenium.find_element(By.ID, "heading").text,
            "Enter a character:",
        )

    def test_submitting_characters_after_category_progresses_game(self):
        self.submit_all("speed", None, None)
        self.p1.wait_for_element_text("heading-smaller")
        self.submit_all(None, "cat", "dog")
        self.p3.wait_for_element_text("heading")
        self.assertEqual(self.p1.selenium.find_element(By.ID, "heading").text, "Vote!")
        self.assertEqual(self.p2.selenium.find_element(By.ID, "heading").text, "Vote!")
        self.assertEqual(self.p3.selenium.find_element(By.ID, "heading").text, "Vote!")

    def test_category_validator_in_boring_mode(self):
        self.p1.selenium.find_element(By.ID, "game-submit").click()
        self.p1.wait_for_element_text("validator")
        self.assertTrue(
            self.p1.selenium.find_element(By.ID, "validator").is_displayed()
        )
        self.assertEqual(
            self.p1.selenium.find_element(By.ID, "validator").text,
            "Enter a longer category...",
        )

    def test_character_validator_in_boring_mode(self):
        self.submit_all("speed", None, None)
        self.p1.wait_for_element_text("heading-smaller")
        self.p2.selenium.find_element(By.ID, "game-submit").click()
        self.p2.wait_for_element_text("validator")
        self.assertTrue(
            self.p2.selenium.find_element(By.ID, "validator").is_displayed()
        )
        self.assertEqual(
            self.p2.selenium.find_element(By.ID, "validator").text,
            "Enter a longer character...",
        )
