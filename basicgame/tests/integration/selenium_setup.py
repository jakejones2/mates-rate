from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from channels.testing import ChannelsLiveServerTestCase  # type: ignore

"""
Selection of test classes with selenium instances available for testing.
Handles the quitting of selenium instances for each test.
"""


def createSeleniumInstance():
    try:
        options = webdriver.ChromeOptions()
        service = Service()
        options.add_argument("--headless=new")
        options.add_argument("--remote-allow-origins=*")
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(5)
        driver.maximize_window()
        return driver
    except:
        raise Exception(
            "Selenium driver failed to initialise, check tests/selenium_setup.py"
        )


class SeleniumTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = createSeleniumInstance()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()


class SeleniumTestTwoUsers(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium_1 = createSeleniumInstance()
        cls.selenium_2 = createSeleniumInstance()

    @classmethod
    def tearDownClass(cls):
        cls.selenium_1.quit()
        cls.selenium_2.quit()
        super().tearDownClass()


class ChannelsSeleniumTestOneUser(ChannelsLiveServerTestCase):
    serve_static = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium_1 = createSeleniumInstance()

    @classmethod
    def tearDownClass(cls):
        cls.selenium_1.quit()
        super().tearDownClass()


class ChannelsSeleniumTestTwoUsers(ChannelsSeleniumTestOneUser):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium_2 = createSeleniumInstance()

    @classmethod
    def tearDownClass(cls):
        cls.selenium_2.quit()
        super().tearDownClass()


class ChannelsSeleniumTestThreeUsers(ChannelsSeleniumTestTwoUsers):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium_3 = createSeleniumInstance()

    @classmethod
    def tearDownClass(cls):
        cls.selenium_3.quit()
        super().tearDownClass()
