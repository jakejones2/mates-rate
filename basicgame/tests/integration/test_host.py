from django.test import TestCase
from django.urls import reverse
from basicgame.tests.integration.selenium_setup import SeleniumTest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from basicgame.models import Game
import re
from selenium.webdriver.support.wait import WebDriverWait


class TestHostView(TestCase):
    """
    Class for testing /host endpoint.
    """

    def test_view_url_exists(self):
        response = self.client.get("/host")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("basicgame:host"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("basicgame:host"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "basicgame/host.html")

    def test_view_uses_correct_context(self):
        response = self.client.get(reverse("basicgame:host"))
        self.assertEqual(response.status_code, 200)
        fhand = open("basicgame/resources/word-ids.txt")
        word_ids = fhand.readlines()
        word_ids = [word.strip() for word in word_ids]
        self.assertTrue(response.context["game_name"] in word_ids)


class TestHostViewPost(TestCase):
    """
    Class for testing the /host POST backend.
    """

    def post_data(self):
        """
        Sends a valid post request to the endpoint.
        """
        self.client.cookies.load({"test-game": "testuser12345678"})
        return self.client.post(
            reverse("basicgame:host"),
            {
                "player-name": "testuser12345678",
                "num-of-cycles": 2,
                "boring": "on",
                "game-name": "test-game",
            },
        )

    def test_creates_game_in_db(self):
        self.post_data()
        self.assertTrue(Game.objects.last().name)
        self.assertEqual(Game.objects.last().cycles, 2)
        self.assertEqual(Game.objects.last().boring, True)
        self.assertEqual(Game.objects.last().host, "testuser12345678")
        self.assertEqual(Game.objects.last().progress, 0)

    def test_post_redirect(self):
        response = self.post_data()
        self.assertEqual(response.status_code, 302)

    def test_redirect_location(self):
        response = self.post_data()
        game_name = Game.objects.last().name
        self.assertEqual(response.url, f"{game_name}/lobby")


class TestHostUI(SeleniumTest):
    """
    Class for testing interactive elements in the host view.
    """

    def setUp(self):
        super().setUp()
        self.selenium.get(f"{self.live_server_url}/host")

    def submit_form(self):
        """
        Completes the host game form via UI.
        """
        self.selenium.get(f"{self.live_server_url}/host")
        self.selenium.find_element(By.ID, "nickname").send_keys("testuser")
        self.selenium.find_element(By.ID, "num-of-cycles").send_keys(Keys.BACKSPACE, 2)
        self.selenium.find_element(By.ID, "boring").click()
        self.selenium.find_element(By.ID, "custom-submit").click()

    def test_cookie_exists(self):
        self.selenium.delete_all_cookies()
        self.submit_form()
        # should be a username cookie
        self.assertEquals(len(self.selenium.get_cookies()), 1)

    def test_nickname_input_exists(self):
        self.assertTrue(self.selenium.find_element(By.ID, "nickname"))

    def test_round_length_input_exists(self):
        self.assertTrue(self.selenium.find_element(By.ID, "num-of-cycles"))

    def test_unpredictable_checkbox_exists(self):
        self.assertTrue(self.selenium.find_element(By.ID, "boring"))

    def test_cookie_content(self):
        self.submit_form()
        cookies = self.selenium.get_cookies()
        regex_pattern = re.compile("testuser[a-zA-Z0-9]{8}")
        cookie_found = False
        for cookie in cookies:
            if regex_pattern.match(cookie["value"]):
                cookie_found = True
        self.assertTrue(cookie_found)

    def test_UI_creates_game_in_db(self):
        self.submit_form()
        regex_userID = re.compile("testuser[a-zA-Z0-9]{8}")
        regex_game_name = re.compile("[a-z]+_[a-z]+")
        self.assertTrue(Game.objects.last())
        try:
            game = Game.objects.last()
            self.assertTrue(regex_userID.match(game.host))
            self.assertTrue(regex_game_name.match(game.name))
            self.assertEqual(game.cycles, 2)
            self.assertTrue(game.boring)
            self.assertEqual(game.progress, 0)
        except Game.DoesNotExist:
            pass

    def test_back_button_creates_new_game_name(self):
        self.submit_form()
        num_of_cookies = len(self.selenium.get_cookies())
        self.selenium.back()
        self.submit_form()
        new_num_of_cookies = len(self.selenium.get_cookies())
        # new game creates a new cookie
        self.assertTrue(new_num_of_cookies == num_of_cookies + 1)

    def test_philosopher_links_to_home_page(self):
        philosopher = self.selenium.find_element(By.ID, "philosopher")
        philosopher.click()
        self.assertEqual(self.selenium.current_url, f"{self.live_server_url}/")

    def test_help_button_exists(self):
        self.assertTrue(self.selenium.find_element(By.ID, "help-button"))

    def test_help_button_works(self):
        self.selenium.find_element(By.ID, "help-button").click()
        self.assertTrue(self.selenium.find_element(By.ID, "help-text").is_displayed())

    def test_close_help_button_works(self):
        self.selenium.find_element(By.ID, "help-button").click()
        self.assertTrue(self.selenium.find_element(By.ID, "close-help").is_displayed())
        self.selenium.find_element(By.ID, "close-help").click()
        self.assertFalse(self.selenium.find_element(By.ID, "help-text").is_displayed())

    def test_nickname_validator(self):
        self.selenium.find_element(By.ID, "num-of-cycles").send_keys(2)
        self.selenium.find_element(By.ID, "custom-submit").click()
        error_message = self.selenium.find_element(By.ID, "form-error")
        self.assertTrue(error_message.is_displayed())
        self.assertEqual(
            error_message.get_attribute("innerHTML"), "Enter a longer nickname..."
        )
        WebDriverWait(self.selenium, 4).until(
            lambda _: not error_message.is_displayed()
        )
        self.assertFalse(error_message.is_displayed())

    def test_rounds_defaults_to_three(self):
        self.assertEqual(
            self.selenium.find_element(By.ID, "num-of-cycles").get_attribute("value"),
            "3",
        )

    def test_rounds_validator(self):
        self.selenium.find_element(By.ID, "nickname").send_keys("John")
        self.selenium.find_element(By.ID, "num-of-cycles").send_keys(Keys.BACKSPACE, 0)
        self.selenium.find_element(By.ID, "custom-submit").click()
        error_message = self.selenium.find_element(By.ID, "form-error")
        self.assertTrue(error_message.is_displayed())
        self.assertEqual(
            error_message.get_attribute("innerHTML"), "Enter a number between 1 and 9"
        )
        self.selenium.find_element(By.ID, "num-of-cycles").send_keys(11)
        self.assertTrue(error_message.is_displayed())
        self.assertEqual(
            error_message.get_attribute("innerHTML"), "Enter a number between 1 and 9"
        )
