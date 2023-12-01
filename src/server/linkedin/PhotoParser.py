from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


class PhotoParser:
    """
    A class to parse profile photos of LinkedIn users.

    :param username: Username of LinkedIn account.
    :type username: str
    :param password: Password of LinkedIn account.
    :type password: str
    """
    def __init__(self, username: str, password: str):
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

    def get_photo(self, profile_url: str) -> str or None:
        """
        Retrieve the profile photo URL from the specified LinkedIn profile URL.

        :param profile_url: LinkedIn profile URL from which to fetch the photo.
        :type profile_url: str

        :return: If a photo is found, returns the URL of the photo; otherwise, returns None.
        :rtype: str
        """
        url = f'{profile_url}/overlay/photo/'
        self.driver.get(url)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        img = soup.find('img', {'class': 'pv-member-photo-modal__content-image evi-image ember-view'})
        if img:
            return img['src']
        return None
