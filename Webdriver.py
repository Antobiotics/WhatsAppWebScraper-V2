from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

"""
This class opens and controls a web browser (for example a Chrome browser).
"""
class Webdriver:

    def __init__(self):
        #self.browser = webdriver.Chrome()  # Create Chrome browser
        #self.browser.maximize_window()

        self.browser = webdriver.Remote(command_executor='http://127.0.0.1:53557',
                                        desired_capabilities={})
        self.browser.session_id = '971023e531a98aac15f0a045dcee0379'
        print self.browser.command_executor._url
        print self.browser.session_id
        #http://127.0.0.1:53557
        #971023e531a98aac15f0a045dcee0379
        #raise RuntimeError("Plof")

    def close(self):
        """
        Close browser
        """
        #self.browser.close()

    def getBrowser(self):
        return self.browser
