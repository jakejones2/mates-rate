from django.test import TestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from basicgame.models import Game, Player
from basicgame.tests.integration.selenium_setup import (
    ChannelsSeleniumTestOneUser,
    ChannelsSeleniumTestTwoUsers,
    ChannelsSeleniumTestThreeUsers,
)


class TestLobbyView(TestCase):
    """
    Class for testing the /:gamename/lobby endpoint.
    """

    def setUp(self):
        super().setUp()
        self.test_game = create_test_game()
        self.client.cookies.load({self.test_game.name: "testuser112345678"})

    def test_view_url_exists(self):
        response = self.client.get("/testgame/lobby")
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get("/testgame/lobby")
        self.assertTemplateUsed(response, "basicgame/lobby.html")

    def test_view_uses_correct_context(self):
        response = self.client.get("/testgame/lobby")
        self.assertEqual(response.context["game_name"], "testgame")
        self.assertEqual(response.context["host"], "testuser112345678")

    def test_redirect_if_game_started_and_not_in_game(self):
        self.test_game.progress = 1
        self.test_game.save()
        response = self.client.get("/testgame/lobby")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/join")


class TestLobbyUIOneUser(ChannelsSeleniumTestOneUser):
    """
    Class for testing interactive elements with one player.
    """

    def setUp(self):
        super().setUp()
        self.test_game = create_test_game()
        add_test_cookie(self.selenium_1, self.live_server_url)
        self.selenium_1.get(f"{self.live_server_url}/{self.test_game}/lobby")

    def test_message_sent_and_received_one_user(self):
        self.selenium_1.find_element(By.ID, "chat-message-input").send_keys("Hi!")
        self.selenium_1.find_element(By.ID, "chat-message-submit").click()
        wait_for_element_text(self.selenium_1, "#chat-log")
        chat_log_value = self.selenium_1.find_element(By.ID, "chat-log").text
        self.assertTrue(chat_log_value.endswith("testuser1: Hi!"))

    def test_cookie_creates_db_player_record_one_user(self):
        wait_for_element_text(self.selenium_1, "#player-log")
        self.assertEqual(Player.objects.last().name, "testuser112345678")
        self.assertEqual(Player.objects.last().game_id, self.test_game)
        self.assertEqual(Player.objects.last().points, 0)
        self.assertFalse(Player.objects.last().submission)
        self.assertFalse(Player.objects.last().votes)

    def test_get_request_without_cookie_redirects(self):
        self.selenium_1.delete_all_cookies()
        self.selenium_1.get(f"{self.live_server_url}/{self.test_game}/lobby")
        wait_for_element_text(self.selenium_1, "h1")
        self.assertEqual(self.selenium_1.current_url, f"{self.live_server_url}/join")

    def test_leave_modal(self):
        self.selenium_1.find_element(By.ID, "philosopher").click()
        self.assertTrue(self.selenium_1.find_element(By.ID, "leave").is_displayed())
        self.selenium_1.find_element(By.ID, "close-leave").click()
        self.assertFalse(self.selenium_1.find_element(By.ID, "leave").is_displayed())
        self.selenium_1.find_element(By.ID, "philosopher").click()
        self.selenium_1.find_element(By.ID, "yes-leave").click()
        self.assertEqual(self.selenium_1.current_url, f"{self.live_server_url}/")

    def test_initial_chat_text(self):
        chat_log = self.selenium_1.find_element(By.ID, "chat-log")
        self.assertEqual(
            chat_log.text,
            "Welcome to the Lobby!\n\nPlease chat whilst waiting\nfor the host to press start.",
        )
        WebDriverWait(self.selenium_1, 10).until(
            lambda _: len(chat_log.text) < 78,
            "welcome text not disappearing",
        )
        self.assertEqual(len(chat_log.text), 0)


class TestLobbyUITwoUsers(ChannelsSeleniumTestTwoUsers):
    """
    Class for testing interactive elements with two players.
    """

    def setUp(self):
        super().setUp()
        self.test_game = create_test_game()
        add_test_cookie(self.selenium_1, self.live_server_url)
        self.selenium_1.get(f"{self.live_server_url}/{self.test_game}/lobby")
        add_test_cookie(
            self.selenium_2, self.live_server_url, value="testuser212345678"
        )
        self.selenium_2.get(f"{self.live_server_url}/{self.test_game}/lobby")
        wait_for_element_text_lines(self.selenium_1, "player-log", 3)

    def send_two_messages(self):
        self.selenium_1.find_element(By.ID, "chat-message-input").send_keys("Hi!")
        self.selenium_1.find_element(By.ID, "chat-message-submit").click()
        self.selenium_2.find_element(By.ID, "chat-message-input").send_keys("Hi!")
        self.selenium_2.find_element(By.ID, "chat-message-submit").click()

    def test_two_users_in_same_lobby(self):
        self.assertTrue(
            self.selenium_2.find_element(By.ID, "player-log").text
            == r"<span style=font-weight:300>players:\n</span>testuser2\ntestuser1"
            or r"<span style=font-weight:300>players:\n</span>testuser1\ntestuser2"
        )

    def test_two_users_can_see_each_others_messages(self):
        self.send_two_messages()
        wait_for_element_text_lines(self.selenium_1, "chat-log", 2)
        wait_for_element_text_lines(self.selenium_2, "chat-log", 2)
        self.assertEqual(
            self.selenium_1.find_element(By.ID, "chat-log").text,
            self.selenium_2.find_element(By.ID, "chat-log").text,
        )
        self.assertTrue(
            self.selenium_1.find_element(By.ID, "chat-log").text.endswith(
                "testuser1: Hi!\ntestuser2: Hi!"
            )
        )

    def test_two_users_from_different_lobbys_cannot_see_each_others_messages(self):
        self.test_game2 = Game.objects.create(
            name="testgame2", cycles=4, boring=False, host="tester", progress=0
        )
        self.selenium_2.add_cookie(
            {"name": self.test_game2.name, "value": "testuser212345678"}
        )
        self.selenium_2.get(f"{self.live_server_url}/{self.test_game2}/lobby")
        self.send_two_messages()
        self.assertNotEqual(
            self.selenium_1.find_element(By.ID, "chat-log").text,
            self.selenium_2.find_element(By.ID, "chat-log").text,
        )
        self.assertTrue(
            self.selenium_1.find_element(By.ID, "chat-log").text.endswith(
                "testuser1: Hi!"
            )
        )
        self.assertTrue(
            self.selenium_2.find_element(By.ID, "chat-log").text.endswith(
                "testuser2: Hi!"
            )
        )


class TestLobbyUIThreeUsers(ChannelsSeleniumTestThreeUsers):
    """
    Class for testing interactive elements with three players.
    """

    def setUp(self):
        super().setUp()
        self.test_game = create_test_game()
        add_test_cookie(
            self.selenium_1, self.live_server_url, value="testuser112345678"
        )
        add_test_cookie(
            self.selenium_2, self.live_server_url, value="testuser212345678"
        )
        add_test_cookie(
            self.selenium_3, self.live_server_url, value="testuser312345678"
        )

    # selenium_1 is the host according to setUp
    def test_host_cant_see_start_game_button_at_first(self):
        self.selenium_1.get(f"{self.live_server_url}/{self.test_game}/lobby")
        self.assertFalse(
            self.selenium_1.find_element(By.ID, "start-game").is_displayed()
        )
        self.assertTrue(
            self.selenium_1.find_element(By.ID, "wait-message").is_displayed()
        )
        self.assertEqual(
            self.selenium_1.find_element(By.ID, "subtitle").text, "Game ID:"
        )

    def test_non_host_sees_correct_wait_message(self):
        self.selenium_2.get(f"{self.live_server_url}/{self.test_game}/lobby")
        self.assertEqual(
            self.selenium_2.find_element(By.ID, "wait-message").text,
            "Waiting for Host...",
        )

    def test_host_sees_correct_wait_message(self):
        self.selenium_1.get(f"{self.live_server_url}/{self.test_game}/lobby")
        self.assertEqual(
            self.selenium_1.find_element(By.ID, "wait-message").text,
            "Waiting for 3 or more players...",
        )

    def test_host_can_see_start_game_when_three_players_ready(self):
        self.selenium_1.get(f"{self.live_server_url}/{self.test_game}/lobby")
        self.selenium_2.get(f"{self.live_server_url}/{self.test_game}/lobby")
        self.selenium_3.get(f"{self.live_server_url}/{self.test_game}/lobby")
        self.assertTrue(
            self.selenium_1.find_element(By.ID, "start-game").is_displayed()
        )

    def test_host_can_start_game_for_all(self):
        self.selenium_1.get(f"{self.live_server_url}/{self.test_game}/lobby")
        self.selenium_2.get(f"{self.live_server_url}/{self.test_game}/lobby")
        self.selenium_3.get(f"{self.live_server_url}/{self.test_game}/lobby")
        self.selenium_1.find_element(By.ID, "start-game").click()
        wait_for_element_text(self.selenium_1, selector="#heading")
        wait_for_element_text(self.selenium_2, selector="#heading")
        wait_for_element_text(self.selenium_3, selector="#heading")
        self.assertEquals(
            self.selenium_1.current_url, f"{self.live_server_url}/{self.test_game}/play"
        )
        self.assertEquals(
            self.selenium_2.current_url, f"{self.live_server_url}/{self.test_game}/play"
        )
        self.assertEquals(
            self.selenium_3.current_url, f"{self.live_server_url}/{self.test_game}/play"
        )


# utils


def create_test_game():
    return Game.objects.create(
        name="testgame",
        cycles=4,
        boring=False,
        host="testuser112345678",
        progress=0,
    )


def wait_for_element_text(driver, selector, error="Selenium cannot find data on page"):
    """
    Wait for a given HTML element's text to appear.
    """
    WebDriverWait(driver, 5).until(
        lambda _: driver.find_element(By.CSS_SELECTOR, selector).text,
        error,
    )


def wait_for_element_text_lines(driver, element_id, num_of_lines):
    """
    Wait for a given number of lines of text to appaer on a given
    HTML element.
    """
    WebDriverWait(driver, 3).until(
        lambda _: len(driver.find_element(By.ID, element_id).text.split("\n"))
        >= num_of_lines,
    )


def add_test_cookie(driver, url, game="testgame", value="testuser112345678"):
    driver.get(f"{url}/")  # need some page open to set cookies
    driver.add_cookie({"name": game, "value": value})
