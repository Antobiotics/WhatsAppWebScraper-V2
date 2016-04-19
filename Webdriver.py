from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

"""
This class opens and controls a web browser (for example a Chrome browser).
"""
class Webdriver:

    """
    Create browser
    """
    def __init__(self):
        self.browser = webdriver.Chrome()  # Create Chrome browser
        self.browser.maximize_window()

    """
    Close browser
    """
    def close(self):
        self.browser.close()

    def getBrowser(self):
        return self.browser

