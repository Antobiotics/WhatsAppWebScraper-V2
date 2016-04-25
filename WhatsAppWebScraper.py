import time
import requests  # todo why erase this?
from selenium.common.exceptions import TimeoutException, \
    StaleElementReferenceException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from Webdriver import Webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as ec
from selenium.webdriver.common.keys import Keys

# ===================================================================
# Server data
SERVER_URL_CHAT = "http://localhost:8888/chat"
SERVER_URL_FINISHED = "http://localhost:8888/chatFinished"
SERVER_POST_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# ===================================================================
# Days of the week
weekDays = ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY')
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
        for i in range(1,4):
            # Debugging purposes
            print("Loading contact number " + str(i))
            startTime = time.time()

            self.browser.implicitly_wait(2) # TODO find a better way to wait for chat to load
            chat = self.loadChat()  # load all conversations for current open chat

            # Get contact name and type (contact/group).
            contactName, contactType = self.getContactDetails(actions)

            # Initialize data item to store messages
            contactData = {"contact": {"name":contactName,"type":contactType},"messages":[]}

            # Get messages from current chat
            print("Get messages for: " + contactName)
            messages = self.getMessages(chat, contactType, contactName)
            contactData['messages'].append(messages)
            print("Got " + str(len(messages)) + " messages.")

            # send to server
            requests.post(SERVER_URL_CHAT, json=contactData, headers=SERVER_POST_HEADERS)

            # Debugging purposes
            totalTime = time.time() - startTime
            print("This took " + str(totalTime) + " seconds.")

            # go to next chat
            self.goToNextContact()

        print("done scraping")

        # send finished signal to server
        requests.post(SERVER_URL_FINISHED, json={}, headers=SERVER_POST_HEADERS)


    def waitForElement(self, cssSelector, timeout=10, cssContainer=None, singleElement=True):
        """
        General helper function. Searches and waits for css element to appear on page and returns it,
        if it doesnt appear after timeout seconds prints relevant exception and returns None.
        """
        # print("Wait for element: " + cssSelector)
        if cssContainer == None:
            cssContainer = self.browser

        try:
            elements = WebDriverWait(cssContainer, timeout).\
                until(ec.presence_of_all_elements_located((By.CSS_SELECTOR,cssSelector)))
            # print("Done waiting for element: " + cssSelector)
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
        # TODO currently loads 10 previous message.
        while counter < 2:
        # while True:
            counter += 1
            btnMore = self.waitForElement(".btn-more", 2)
            if btnMore != None:
                try:
                    actions.click(btnMore).perform()
                except StaleElementReferenceException as e:
                    print(e.msg)
                    break
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
            contactType = "person"
        else:
            contactType = "group"

        return contactName, contactType

    def getMessages(self, chat, contactType, contactName):
        # TODO this logic is very very slow - make it faster.

        messageElements = self.waitForElement(".msg",10,None,False)
        messages = []
        name, text, time = None, None, None
        lastDay = "4/7/2014"

        for msg in messageElements:

            # Incoming/Outgoing message
            textContainer = self.getElement(".selectable-text",msg)
            if  textContainer != None:
                # Get text and time
                text = textContainer.text
                time = msg.find_element_by_css_selector(".message-datetime").text + ", " + lastDay

                # Incoming message case
                if self.getElement(".message-in", msg):
                    if contactType == 'person':
                        name = contactName
                    else:
                        name = self.getElement(".message-author", msg)
                        if name is None:
                            name = lastName
                        else:
                            name = str(name.text).replace("\u2060","")
                            lastName = name

                # Outgoing message case
                elif self.getElement(".message-out",msg) != None:
                    name = "Me"

                msgData = {"name":name, "text": text, "time":time}
                messages.append(msgData)
                # print(msgData)

            # System date message
            elif self.getElement(".message-system", msg) != None:
                    # Check that it's not a contact leaving/exiting group
                if msg.text in weekDays:
                    lastDay = str(msg.text).replace("\u2060","")
                    lastName = contactName

            # Unsupported message type (image, video, audio...), we do not return these.
            else:
                continue

        return messages

