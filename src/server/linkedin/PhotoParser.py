from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchDriverException
from webdriver_manager.chrome import ChromeDriverManager


class PhotoParser:
    def __init__(self, username, password):
        self.__username = username
        self.__password = password

        self._init_driver()
        self._login()

    def _init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')

        try:
            # Attempt to initialize the Chrome WebDriver without reinstalling ChromeDriver
            driver = webdriver.Chrome(options=chrome_options)
        except NoSuchDriverException:
            # If an exception occurs (indicating that the driver is not installed), install it
            print("ChromeDriver not found. Installing...")
            ChromeDriverManager().install()
            print("ChromeDriver installed successfully. Initializing WebDriver...")
            # Now try to initialize the WebDriver again
            driver = webdriver.Chrome(options=chrome_options)
        self.driver = driver

    def _login(self):
        self.driver.get('https://www.linkedin.com/login')
        self.driver.find_element('id', 'username').send_keys(self.__username)
        self.driver.find_element('id', 'password').send_keys(self.__password)
        self.driver.find_element('css selector', '.btn__primary--large').click()
