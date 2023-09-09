from django.test import TestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from basicgame.models import Game, Player
from basicgame.tests.integration.base import ThreePlayerTestGame


class TestPlayView(TestCase):
    """
    Class for testing the play view endpoint.
    """

    def setUp(self):
        super().setUp()
        self.test_game = Game.objects.create(
            name="testgame", cycles=4, boring=False, host="test", progress=1
        )
        self.user1 = Player.objects.create(
            name="testuser1",
            game_id=self.test_game,
            points=0,
            submission=None,
            votes=None,
        )

    def test_view_url_exists(self):
        response = self.client.get("/testgame/play")
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get("/testgame/play")
        self.assertTemplateUsed(response, "basicgame/play.html")

    def test_view_uses_correct_context(self):
        response = self.client.get("/testgame/play")
        self.assertEqual(response.context["game_name"], "testgame")
        self.assertEqual(response.context["host"], "test")


class TestPlayData(ThreePlayerTestGame):
    """
    Class for testing the play view html data and cookie behvaiour.
    """

    def test_page_contains_correct_game_data(self):
        self.player_one_start_game()
        game_name = self.p1.selenium.find_element(By.ID, "game-name").get_attribute(
            "innerHTML"
        )
        players = self.p1.selenium.find_element(By.ID, "players").get_attribute(
            "innerHTML"
        )
        host = self.p1.selenium.find_element(By.ID, "game-host").get_attribute(
            "innerHTML"
        )
        self.assertEqual(
            players, '["testuser112345678", "testuser212345678", "testuser312345678"]'
        )
        self.assertEqual(host, '"testuser112345678"')
        self.assertEqual(game_name, '"testgame"')
        self.assertTrue(self.p1.selenium.find_element(By.ID, "character-hints"))
        self.assertTrue(self.p1.selenium.find_element(By.ID, "category-hints"))

    def test_using_wrong_cookie_generates_alert(self):
        self.p1.selenium.get(f"{self.live_server_url}/")
        self.p1.selenium.add_cookie(
            {"name": self.test_game.name, "value": "testuser412345678"}
        )
        self.p1.selenium.get(f"{self.live_server_url}/{self.test_game.name}/play")
        self.assertEquals(
            self.p1.selenium.switch_to.alert.text,
            "You are not a member of this game and cannot partake! GO AWAY!",
        )


class TestPlayUI(ThreePlayerTestGame):
    """
    Class for testing the interactive features of the initial play view,
    aside from the gameplay itself.
    """

    def test_help_box_initially_pops_up_and_closes(self):
        self.player_one_start_game(close_help=False)
        help_text = self.p1.selenium.find_element(By.ID, "help-text")
        self.assertTrue(help_text)
        self.p1.wait_for_hidden("help-text", 5, invert=True)
        self.assertTrue(help_text.is_displayed())
        self.p1.wait_for_hidden("help-text", 10)
        self.assertFalse(help_text.is_displayed())

    def test_help_button_works_after_initial_popup(self):
        self.player_one_start_game(close_help=False)
        self.p1.wait_for_hidden("help-text", 5, invert=True)
        self.p1.wait_for_hidden("help-text", 10)
        button = self.p1.selenium.find_element(By.ID, "help-button")
        self.assertTrue(button)
        button.click()
        help_text = self.p1.selenium.find_element(By.ID, "help-text")
        self.assertTrue(help_text.is_displayed())
        self.p1.selenium.find_element(By.ID, "close-help").click()
        self.assertFalse(help_text.is_displayed())

    def test_leave_modal(self):
        self.player_one_start_game()
        self.p1.selenium.find_element(By.ID, "philosopher").click()
        self.assertTrue(self.p1.selenium.find_element(By.ID, "leave").is_displayed())
        self.p1.selenium.find_element(By.ID, "close-leave").click()
        self.assertFalse(self.p1.selenium.find_element(By.ID, "leave").is_displayed())
        self.p1.selenium.find_element(By.ID, "philosopher").click()
        self.p1.selenium.find_element(By.ID, "yes-leave").click()
        self.assertEqual(self.p1.selenium.current_url, f"{self.live_server_url}/")

    def test_philosopher_hints_different_for_category_and_character_picker(self):
        self.start_three_player_game()
        self.p1.wait_for_element_text("speech")
        player_one_hint = self.p1.selenium.find_element(By.ID, "speech").text
        self.p2.wait_for_element_text("speech")
        player_two_hint = self.p2.selenium.find_element(By.ID, "speech").text
        self.assertNotEqual(player_one_hint, player_two_hint)

    def test_philosopher_hints_change_over_time(self):
        self.player_one_start_game()
        self.p1.wait_for_element_text("speech")
        hint1 = self.p1.selenium.find_element(By.ID, "speech").text
        self.p1.wait_for_text_change("speech", hint1, 15)
        hint2 = self.p1.selenium.find_element(By.ID, "speech").text
        self.assertNotEqual(hint1, hint2)

    def test_game_footer_changes(self):
        self.player_one_start_game()
        self.p1.wait_for_element_text("game-name-footer")
        game_name = self.p1.selenium.find_element(By.ID, "game-name-footer").text
        self.p1.wait_for_text_change("game-name-footer", game_name, 8)
        current_round = self.p1.selenium.find_element(By.ID, "game-name-footer").text
        self.assertTrue(game_name.startswith("Game ID: "))
        self.assertTrue(current_round.startswith("Round"))
