from django.test import TestCase
from django.urls import reverse
from basicgame.tests.integration.selenium_setup import SeleniumTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class TestHomeView(TestCase):
    """
    Class for testing root endpoint.
    """

    def test_view_url_exists(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("basicgame:home"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("basicgame:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "basicgame/home.html")


class TestHomeUI(SeleniumTest):
    """
    Class for testing interactive elements of home view.
    """

    def setUp(self):
        super().setUp()
        self.selenium.get(f"{self.live_server_url}/")
        self.join_game_button = self.selenium.find_element(By.ID, "join-game")
        self.host_game_button = self.selenium.find_element(By.ID, "host-game")
        self.help_button = self.selenium.find_element(By.ID, "help-button")
        self.help_text = self.selenium.find_element(By.ID, "help-text")
        self.close_help_button = self.selenium.find_element(By.ID, "close-help")
        self.right_speech = self.selenium.find_element(By.ID, "speech-right")
        self.left_speech = self.selenium.find_element(By.ID, "speech-left")

    def test_join_button_exists(self):
        self.assertTrue(self.join_game_button)

    def test_host_button_exists(self):
        self.assertTrue(self.host_game_button)

    def test_join_button_works(self):
        self.join_game_button.click()
        self.assertEqual(self.selenium.current_url, f"{self.live_server_url}/join")

    def test_host_button_works(self):
        self.host_game_button.click()
        self.assertEqual(self.selenium.current_url, f"{self.live_server_url}/host")

    def test_help_button_exists(self):
        self.assertTrue(self.help_button)

    def test_help_button_works(self):
        self.help_button.click()
        self.assertTrue(self.help_text.is_displayed())

    def test_close_help_button_works(self):
        self.help_button.click()
        self.assertTrue(self.close_help_button.is_displayed())
        self.close_help_button.click()
        self.assertFalse(self.help_text.is_displayed())

    def test_philosopher(self):
        self.assertEqual(self.right_speech.get_attribute("innerHTML"), "Play my game!")
        WebDriverWait(self.selenium, 10).until(
            lambda _: self.left_speech.get_attribute("innerHTML")
            and self.left_speech.get_attribute("innerHTML")
            == "Rate your friends in funny categories",
            "new hint not loaded",
        )
        WebDriverWait(self.selenium, 15).until(
            lambda _: self.right_speech.get_attribute("innerHTML")
            and self.right_speech.get_attribute("innerHTML") != "Play my game!",
        )

    def test_philosopher_click(self):
        self.assertEqual(self.right_speech.get_attribute("innerHTML"), "Play my game!")
        philosopher = self.selenium.find_element(By.ID, "philosopher")
        philosopher.click()
        philosopher.click()
        WebDriverWait(self.selenium, 5).until(
            lambda _: self.right_speech.get_attribute("innerHTML") != "Play my game!",
        )
        self.assertNotEqual(
            self.right_speech.get_attribute("innerHTML"), "Play my game!"
        )
