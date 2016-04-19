import json

from selenium.common.exceptions import WebDriverException, TimeoutException, \
    StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

import Scripts
from Webdriver import Webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as ec
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys


WHATSAPP_CHAT_PAGE_ELEMENT = ".infinite-list-viewport"
WHATSAPP_WEBSITE = "https://web.whatsapp.com/"

class WhatsAppWebScraper:

    def __init__(self, webdriver):
        self.browser = Webdriver.getBrowser(webdriver)  # Get browser
        self.browser.set_page_load_timeout(150)  # Set timeout to 150 seconds
        self.browser.get(WHATSAPP_WEBSITE)  # Navigate browser to WhatsApp page

        # Wait in current page for user to log in using barcode scan.
        self.browserWaitForAndGetElement(WHATSAPP_CHAT_PAGE_ELEMENT)


    def scrape(self):
        print("start scraping")

        actions = ActionChains(self.browser)  # init actions option

        # Get to first contact chat
        searchBox = self.browserWaitForAndGetElement(".input.input-search")
        actions.click(searchBox).send_keys(Keys.ARROW_DOWN).perform()

        chat = self.loadChat()  # load all conversations for current open chat

        # Get contact name and type (contact/group).
        contactName, contactType = self.getContactDetails(actions)

        # Get messages

        # Initialize data item to store messages
        contactData = {"contact": {"name":contactName,"type":contactType},"messages":[]}

        # JSON it all
        jsonContactData = json.dump()
        # send to server

        # go to next chat
        self.goToNextContact()

        # {"name":"asaf", "text":"hi moses!", "time":"5:22 PM, 4/7/2016"},
        print("done scraping")
        pass

    # Wait for css element to appear on page and return it, if it doesnt appear after timeout seconds
    # close browser and exit program
    def browserWaitForAndGetElement(self, cssSelector, timeout=120):
        try:
            element = WebDriverWait(self.browser, timeout).\
                until(ec.presence_of_element_located((By.CSS_SELECTOR,cssSelector)))
            return element
        except TimeoutException:
            print("Timed out waiting for element " + str(cssSelector) + " on page: " + str(self.browser.current_url))
            return None

    """
    Get all message for current open chat.
    """
    def loadChat(self):
        actions = ActionChains(self.browser)  # init actions
        chat = self.browserWaitForAndGetElement(".message-list")  # wait for chat to load
        actions.click(chat)
        counter = 0
        # load counter previous messages or until no "btn-more" exists
        # TODO currently loads 10 previous message. Decide whether this needs to change.
        while counter < 10:
            counter += 1
            btnMore = self.browserWaitForAndGetElement(".btn-more", 2)
            if btnMore != None:
                try:
                    actions.click(btnMore).perform()
                except StaleElementReferenceException:
                    continue
            else:
                break
        return chat

    # Goes to next contact chat in contact list
    def goToNextContact(self, actions):
        searchBox = self.browserWaitForAndGetElement(".input.input-search")
        actions.click(searchBox).send_keys(Keys.TAB).send_keys(Keys.ARROW_DOWN).perform()

    # Get contact name and type (contact/group). This is done by clicking on Chat Menu button and
    # opening a submenu which contains the word Contact or Group and extracting that word.
    def getContactDetails(self, actions):
        # Get contact name
        contactName = self.browser.find_element_by_css_selector("#main header div.chat-body "
                                                                "div.chat-main h2 span").text
        # Open chat menu
        chatMenu = self.browser.find_element_by_id("main").find_element_by_css_selector(
                ".icon-menu")
        actions.click(chatMenu).perform()

        # Get first field which has contact/group info
        contactTypeIdentifier = chatMenu.find_element_by_xpath('//*[@id="main"]/header/div[3]/div/div[2]/span/div/ul/li[1]/a').text
        if "Contact" in contactTypeIdentifier:
            contactType = "Contact"
        else:
            contactType = "Group"

        return contactName, contactType