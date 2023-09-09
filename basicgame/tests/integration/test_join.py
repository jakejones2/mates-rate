from django.test import TestCase
from django.urls import reverse
from basicgame.tests.integration.selenium_setup import (
    SeleniumTest,
    SeleniumTestTwoUsers,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from basicgame.models import Game, Player
import re


class TestJoinView(TestCase):
    """
    Class for testing /join endpoint.
    """

    def test_view_url_exists(self):
        response = self.client.get("/join")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("basicgame:join"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("basicgame:join"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "basicgame/join.html")


class TestJoinViewPost(TestCase):
    """
    Class for testing the POST backend for /join.
    """

    def setUp(self):
        super().setUp()
        self.test_game = Game.objects.create(
            name="test", cycles=4, boring=False, host="test", progress=0
        )

    def post_data(self):
        """
        Sends valid POST request to join backend.
        """
        self.client.cookies.load({self.test_game.name: "testname12345678"})
        return self.client.post(
            reverse("basicgame:join"),
            {"player-name": "testname12345678", "game-name": self.test_game.name},
        )

    def test_creates_player_in_db(self):
        self.post_data()
        self.assertEqual(Player.objects.last().name, "testname12345678")
        self.assertEqual(Player.objects.last().game_id, self.test_game)
        self.assertEqual(Player.objects.last().points, 0)
        self.assertEqual(Player.objects.last().submission, None)
        self.assertEqual(Player.objects.last().votes, None)

    def test_redirect(self):
        response = self.post_data()
        self.assertEqual(response.status_code, 302)

    def test_redirect_location(self):
        response = self.post_data()
        self.assertEqual(response.url, f"{self.test_game.name}/lobby")


class TestJoinUI(SeleniumTest):
    """
    Class for testing interactive elements in join view.
    """

    def setUp(self):
        super().setUp()
        self.test_game = Game.objects.create(
            name="test", cycles=4, boring=False, host="test", progress=0
        )
        self.selenium.get(f"{self.live_server_url}/join")

    def test_nickname_input_exists(self):
        self.assertTrue(self.selenium.find_element(By.ID, "nickname"))

    def test_game_input_exists(self):
        self.assertTrue(self.selenium.find_element(By.ID, "game-name"))

    def test_number_of_visible_elements(self):
        elements = [
            element for element in self.selenium.find_elements(By.CSS_SELECTOR, "*")
        ]
        displayed_elements = [element for element in elements if element.is_displayed()]
        self.assertEqual(len(displayed_elements), 13)

    def test_cookie_exists(self):
        self.selenium.delete_all_cookies()
        post_join_data(self.selenium, self.live_server_url)
        # should be no other coookies
        self.assertEquals(len(self.selenium.get_cookies()), 1)

    def test_player_name_field_hidden(self):
        self.assertFalse(
            self.selenium.find_element(By.ID, "player-name").is_displayed()
        )

    def test_cookie_content(self):
        self.selenium.delete_all_cookies()
        post_join_data(self.selenium, self.live_server_url)
        regex_userID = re.compile("testuser[a-zA-Z0-9]{8}")
        cookies = self.selenium.get_cookies()
        for cookie in cookies:
            if not cookie["name"] == "csrftoken":
                self.assertEqual(cookie["name"], "test")
                self.assertTrue(regex_userID.match(cookie["value"]))

    def test_game_validator(self):
        post_join_data(self.selenium, self.live_server_url, "bob", "fish_cake")
        self.assertEqual(
            self.selenium.find_element(By.ID, "form-error").text,
            "Game does not exist!",
        )

    def test_nickname_validator(self):
        post_join_data(self.selenium, self.live_server_url, "", "test")
        self.assertEqual(
            self.selenium.find_element(By.ID, "form-error").text,
            "Longer nickname please...",
        )

    def test_game_started_validator(self):
        self.test_game.progress = 1
        self.test_game.save()
        post_join_data(self.selenium, self.live_server_url, "bob", "test")
        self.assertEqual(
            self.selenium.find_element(By.ID, "form-error").text,
            "Game already started!",
        )

    def test_joining_takes_straight_to_game_after_start(self):
        post_join_data(self.selenium, self.live_server_url, "bob", "test")
        self.test_game.progress = 1
        self.test_game.save()
        self.selenium.get(f"{self.live_server_url}/join")
        post_join_data(self.selenium, self.live_server_url, "bob", "test")
        self.assertEqual(self.selenium.current_url, f"{self.live_server_url}/test/play")

    def test_ability_two_play_two_games_at_once(self):
        game2 = Game.objects.create(
            name="test2", cycles=4, boring=False, host="test", progress=0
        )
        game2.save()
        self.selenium.delete_all_cookies()
        post_join_data(self.selenium, self.live_server_url, "bob", "test")
        self.assertEqual(
            self.selenium.current_url, f"{self.live_server_url}/test/lobby"
        )
        self.selenium.get(f"{self.live_server_url}/join")
        post_join_data(self.selenium, self.live_server_url, "bob", "test2")
        self.assertEqual(
            self.selenium.current_url, f"{self.live_server_url}/test2/lobby"
        )
        self.test_game.progress = 1
        self.test_game.save()
        self.selenium.get(f"{self.live_server_url}/join")
        post_join_data(self.selenium, self.live_server_url, "bob", "test")
        self.assertEqual(self.selenium.current_url, f"{self.live_server_url}/test/play")

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

    def test_game_id_case_insensitive_and_allows_hyphens(self):
        self.test_game = Game.objects.create(
            name="test_game", cycles=4, boring=False, host="test", progress=0
        )
        post_join_data(self.selenium, self.live_server_url, "bob", "TeSt-GamE")
        self.assertEqual(
            self.selenium.current_url, f"{self.live_server_url}/test_game/lobby"
        )


class TestTwoNicknamesValidator(SeleniumTestTwoUsers):
    """
    Class for testing two players interacting with join view.
    """

    def setUp(self):
        super().setUp()
        self.test_game = Game.objects.create(
            name="test", cycles=4, boring=False, host="test", progress=0
        )

    def test_two_identical_nicknames_validator(self):
        post_join_data(self.selenium_1, self.live_server_url, "mike", "test")
        self.selenium_2.delete_all_cookies()
        post_join_data(self.selenium_2, self.live_server_url, "mike", "test")
        WebDriverWait(self.selenium_2, 5).until(
            lambda _: self.selenium_2.find_element(By.ID, "form-error").text,
            f"element with ID='form-error' innerHTML not yet appeared",
        )
        self.assertEqual(
            self.selenium_2.find_element(By.ID, "form-error").text,
            "Nickname already taken!",
        )


# utils


def post_join_data(driver, url, nickname="testuser", game="test"):
    """
    Posts the given join data via selenium driver.
    """
    driver.get(f"{url}/join")
    WebDriverWait(driver, 5).until(
        lambda _: driver.find_element(By.ID, "nickname-label").text,
        f"element with ID='nickname-label innerHTML not yet appeared",
    )
    driver.find_element(By.ID, "nickname").send_keys(nickname)
    driver.find_element(By.ID, "game-name").send_keys(game)
    driver.find_element(By.ID, "custom-submit").click()
