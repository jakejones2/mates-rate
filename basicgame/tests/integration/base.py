from channels.testing import ChannelsLiveServerTestCase  # type: ignore
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from basicgame.models import Game, Player
from basicgame.tests.integration.selenium_setup import createSeleniumInstance


class TestPlayer:
    """
    Class representing a test player with methods representing
    behaviours in the game. Has own selenium instance.
    """

    def __init__(self, number):
        self.number = number
        self.selenium = createSeleniumInstance()

    def seed_data(self, game):
        self.data = Player.objects.create(
            name=f"testuser{self.number}12345678",
            game_id=game,
            points=0,
            submission=None,
            votes=None,
        )

    def add_submission(self, submission):
        self.data.submission = submission
        self.data.save()

    def remove_submission(self):
        self.data.submission = None
        self.data.save()

    def add_vote(self, vote):
        self.data.votes = vote
        self.data.save()

    def remove_vote(self):
        self.data.votes = None
        self.data.save()

    def wait_for_element_text(self, id, time=5):
        """
        Wait until the text property of a given HTML element has loaded.
        """
        WebDriverWait(self.selenium, time).until(
            lambda _: self.selenium.find_element(By.ID, id).text,
            f"element with ID={id} innerHTML not yet loaded",
        )

    def wait_for_text_change(self, id, string, time=5):
        """
        Wait until the text property of an HTML element differs
        from the given string.
        """
        WebDriverWait(self.selenium, time).until(
            lambda _: self.selenium.find_element(By.ID, id).text != string,
            f"text value of element with ID={id} has not changed",
        )

    def wait_for_hidden(self, id, time=5, invert=False):
        """
        Wait for an HTML element to be hidden.
        """
        if invert:
            WebDriverWait(self.selenium, time).until(
                lambda _: self.selenium.find_element(By.ID, id).is_displayed(),
                f"element with ID={id} is not displayed",
            )
        else:
            WebDriverWait(self.selenium, time).until(
                lambda _: not self.selenium.find_element(By.ID, id).is_displayed(),
                f"element with ID={id} is still displayed",
            )

    def submit_game_text(self, text):
        self.selenium.find_element(By.ID, "game-input").send_keys(text)
        self.selenium.find_element(By.ID, "game-submit").click()

    def submit_game_text_and_wait(self, text, changeid, changevalue):
        """
        Enter text into the game submission and click send. Then wait
        for a given element's text to change (e.g. wait for the heading
        to change from 'Waiting for other players' to 'Vote!')
        """
        self.selenium.find_element(By.ID, "game-input").send_keys(text)
        self.selenium.find_element(By.ID, "game-submit").click()
        self.wait_for_text_change(changeid, changevalue)


class ThreePlayerGameBase(ChannelsLiveServerTestCase):
    """
    Base class for initialising a three-player test game.
    Selenium persists between tests for performance but player data
    does not.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.p1 = TestPlayer(1)
        cls.p2 = TestPlayer(2)
        cls.p3 = TestPlayer(3)
        cls.players = [cls.p1, cls.p2, cls.p3]

    @classmethod
    def tearDownClass(cls):
        for player in cls.players:
            player.selenium.quit()
        return super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.test_game = Game.objects.create(
            name="testgame",
            cycles=2,
            boring=False,
            host="testuser112345678",
            progress=1,
        )
        for player in self.players:
            player.seed_data(self.test_game)

    def add_submissions(self, sub1, sub2, sub3):
        if sub1:
            self.p1.add_submission(sub1)
        if sub2:
            self.p2.add_submission(sub2)
        if sub3:
            self.p3.add_submission(sub3)

    def remove_all_submissions(self):
        for player in self.players:
            player.remove_submission()

    def add_votes(self, sub1, sub2, sub3):
        if sub1:
            self.p1.add_vote(sub1)
        if sub2:
            self.p2.add_vote(sub2)
        if sub3:
            self.p3.add_vote(sub3)

    def remove_all_votes(self):
        for player in self.players:
            player.remove_vote()

    def submit_all(self, text1, text2, text3):
        if text1:
            self.p1.submit_game_text(text1)
        if text2:
            self.p2.submit_game_text(text2)
        if text3:
            self.p3.submit_game_text(text3)


class ThreePlayerTestGame(ThreePlayerGameBase):
    """
    Extends the three-player base test game for a normal game
    (boring = false).
    """

    def setUp(self):
        super().setUp()

    def start_three_player_game(
        self, wait_for_element="heading", time=5, close_help=True
    ):
        """
        Retrieves home url, adds game cookie, then retrieves game url
        and waits for it to load.
        """
        self.p1.selenium.get(f"{self.live_server_url}/")
        self.p1.selenium.add_cookie(
            {"name": self.test_game.name, "value": "testuser112345678"}
        )
        self.p1.selenium.get(f"{self.live_server_url}/{self.test_game.name}/play")
        self.p1.wait_for_element_text(wait_for_element, time)

        self.p2.selenium.get(f"{self.live_server_url}/")
        self.p2.selenium.add_cookie(
            {"name": self.test_game.name, "value": "testuser212345678"}
        )
        self.p2.selenium.get(f"{self.live_server_url}/{self.test_game.name}/play")
        self.p2.wait_for_element_text(wait_for_element, time)

        self.p3.selenium.get(f"{self.live_server_url}/")
        self.p3.selenium.add_cookie(
            {"name": self.test_game.name, "value": "testuser312345678"}
        )
        self.p3.selenium.get(f"{self.live_server_url}/{self.test_game.name}/play")
        self.p3.wait_for_element_text(wait_for_element, time)

        if close_help:
            self.p1.selenium.find_element(By.ID, "close-help").click()
            self.p2.selenium.find_element(By.ID, "close-help").click()
            self.p3.selenium.find_element(By.ID, "close-help").click()

    def player_one_start_game(
        self, wait_for_element="heading", time=5, close_help=True
    ):
        """
        Same as above but just for one player.
        """
        self.p1.selenium.get(f"{self.live_server_url}/")
        self.p1.selenium.add_cookie(
            {"name": self.test_game.name, "value": "testuser112345678"}
        )
        self.p1.selenium.get(f"{self.live_server_url}/{self.test_game.name}/play")
        self.p1.wait_for_element_text(wait_for_element, time)

        if close_help:
            self.p1.selenium.find_element(By.ID, "close-help").click()


class BoringThreePlayerTestGame(ThreePlayerGameBase):
    """
    Extends the three-player test game base for a boring game.
    """

    def setUp(self):
        super().setUp()
        self.test_game.boring = True
        self.test_game.save()

    def start_three_player_game(self, time=5, close_help=True):
        self.p1.selenium.get(f"{self.live_server_url}/")
        self.p1.selenium.add_cookie(
            {"name": self.test_game.name, "value": "testuser112345678"}
        )
        self.p1.selenium.get(f"{self.live_server_url}/{self.test_game.name}/play")
        self.p1.wait_for_element_text("heading", time)

        self.p2.selenium.get(f"{self.live_server_url}/")
        self.p2.selenium.add_cookie(
            {"name": self.test_game.name, "value": "testuser212345678"}
        )
        self.p2.selenium.get(f"{self.live_server_url}/{self.test_game.name}/play")
        self.p2.wait_for_element_text("heading-smaller", time)

        self.p3.selenium.get(f"{self.live_server_url}/")
        self.p3.selenium.add_cookie(
            {"name": self.test_game.name, "value": "testuser312345678"}
        )
        self.p3.selenium.get(f"{self.live_server_url}/{self.test_game.name}/play")
        self.p3.wait_for_element_text("heading-smaller", time)

        if close_help:
            self.p1.selenium.find_element(By.ID, "close-help").click()
            self.p2.selenium.find_element(By.ID, "close-help").click()
            self.p3.selenium.find_element(By.ID, "close-help").click()
