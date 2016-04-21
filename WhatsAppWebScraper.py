import json
import requests
import time
from selenium.common.exceptions import WebDriverException, TimeoutException, \
    StaleElementReferenceException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
import Scripts
from Webdriver import Webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as ec
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys

# ===================================================================
# Server data
SERVER_URL_CHAT = "http://localhost:8888/chat"
SERVER_POST_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# ===================================================================


class WhatsAppWebScraper:
    """
    Main class for scraping whatsapp. Receives open browser, goes to WhatsApp Web page, scrapes data
    and sends one contact at a time to the server.
    """

    def __init__(self, webdriver):
        self.browser = Webdriver.getBrowser(webdriver)  # Get browser
        self.browser.set_page_load_timeout(150)  # Set timeout to 150 seconds
        self.browser.get("https://web.whatsapp.com/")  # Navigate browser to WhatsApp page

        # Wait in current page for user to log in using barcode scan.
        self.waitForElement(".infinite-list-viewport",30)


    def scrape(self):
        print("start scraping")

        actions = ActionChains(self.browser)  # init actions option

        # Get to first contact chat
        searchBox = self.waitForElement(".input.input-search")
        actions.click(searchBox).send_keys(Keys.TAB).perform()

        # Scrape each chat
        for i in range(1,6):
            print("Loading contact number " + str(i))

            self.browser.implicitly_wait(2) # TODO check if this is useful
            chat = self.loadChat()  # load all conversations for current open chat

            # Get contact name and type (contact/group).
            contactName, contactType = self.getContactDetails(actions)

            # Initialize data item to store messages
            contactData = {"contact": {"name":contactName,"type":contactType},"messages":[]}

            # Get messages from current chat
            print("Get messages")
            messages = self.getMessages(chat, contactType, contactName)
            contactData['messages'].append(messages)
            print("Finished getting messages")

            # send to server
            requests.post(SERVER_URL_CHAT, json=contactData, headers=SERVER_POST_HEADERS)

            # go to next chat
            self.goToNextContact()

        print("done scraping")


    def waitForElement(self, cssSelector, timeout=10, cssContainer=None, singleElement=True):
        """
        General helper function. Searches and waits for css element to appear on page and returns it,
        if it doesnt appear after timeout seconds prints relevant exception and returns None.
        """
        print("Wait for element: " + cssSelector)
        if cssContainer == None:
            cssContainer = self.browser

        try:
            elements = WebDriverWait(cssContainer, timeout).\
                until(ec.presence_of_all_elements_located((By.CSS_SELECTOR,cssSelector)))
            print("Done waiting for element: " + cssSelector)
            if singleElement:
                return elements[0]
            return elements
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            print("Exception for element "+str(cssSelector)+" on page: "+str(self.browser.current_url))
            return None

    def getElement(self, cssSelector, cssContainer = None):
        """
        Helper function. Searches for element by css selector, if it doesn't exists catchs
        NoSuchElementException and
        returns None.
        """
        if cssContainer == None:
            cssContainer = self.browser
        try:
            return cssContainer.find_element_by_css_selector(cssSelector)
        except (NoSuchElementException, StaleElementReferenceException):
            return None

    def loadChat(self):
        """
        Get all message for current open chat.
        """
        print("Load chat")
        actions = ActionChains(self.browser)  # init actions
        chat = self.waitForElement(".message-list")  # wait for chat to load
        actions.click(chat).perform()

        counter = 0
        # load counter previous messages or until no "btn-more" exists
        # TODO currently loads 2 previous message. Decide whether this needs to change.
        while counter < 2:
            counter += 1
            btnMore = self.waitForElement(".btn-more", 2)
            if btnMore != None:
                try:
                    actions.click(btnMore).perform()
                except StaleElementReferenceException:
                    continue
            else:
                break
        # return chat

    def goToNextContact(self, isFirst = False):
        """
        Goes to next contact chat in contact list
        """
        actions = ActionChains(self.browser)
        print("GO TO NEXT CONTACT")
        actions.click(self.waitForElement(".input.input-search")).perform()
        actions.send_keys(Keys.TAB).send_keys(Keys.ARROW_DOWN).perform()
        # actions.click(self.waitForElement("main")).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.ARROW_DOWN).perform()
        # actions.click(self.waitForElement(".pane-chat-msgs")).perform()

    def getContactDetails(self, actions):
        """
        Get contact name and type (contact/group). This is done by clicking on Chat Menu button and
        opening a submenu which contains the word Contact or Group and extracting that word.
        """
        # Get contact name
        # TODO maybe make this selector less specific to match possible page variations
        contactName = self.browser.find_element_by_css_selector("#main header div.chat-body "
                                                                "div.chat-main h2 span").text
        # # Open chat menu. Waits only 5 seconds for it to load.
        # chatMenu = self.clickOnDynamicElement(actions, "#main .icon-menu")

        # If this is a contact chat then this field will not appear
        if self.getElement(".msg-group") == None:
            contactType = "Contact"
        else:
            contactType = "Group"

        return contactName, contactType

    def getMessages(self, chat, contactType, contactName):
        # TODO this logic is very very slow - make it faster.
        # by: 1) split to incoming and outgoing 2) put most likely first 3) remove contains and stuff

        # TODO this needs to change - it only wait for one message to load, not all of them.
        messageElements = self.waitForElement(".msg",10,None,False)
        messages = []
        name, text, time = None, None, None
        lastDay = "11/11/1111" # TODO validate with server people

        for msg in messageElements:

            # System date message
            if self.getElement(".message-system", msg) != None:
                # TODO fix case where last day is name of day and not date (for example SUNDAY)
                # Check that it's not a contact leaving/exiting group
                if "joined" not in msg.text and "left" not in msg.text:
                    lastDay = str(msg.text).replace("\u2060","")
                    lastName = contactName

            # Incoming/Outgoing message
            elif self.getElement(".selectable-text",msg) != None:
                # Get text and time
                text = msg.find_element_by_css_selector(".selectable-text").text
                # TODO add AM/PM
                time = msg.find_element_by_css_selector(".message-datetime").text + ", " + lastDay

                # Outgoing message case
                if self.getElement(".message-out",msg) != None:
                    name = "Me" # TODO make sure this value is confirmed with server people

                # Incoming message case
                elif self.getElement(".message-in", msg):
                    if contactType == 'Contact':
                        name = contactName
                    else:
                        name = self.getElement(".message-author", msg)
                        if name == None:
                            name = lastName
                        else:
                            name = str(name.text).replace("\u2060","")
                            lastName = name

                msgData = {"name":name, "text": text, "time":time}
                messages.append(msgData)
                print(msgData)

            # Unsupported message type (image, video, audio...), we do not return these.
            else:
                continue

        return messages

