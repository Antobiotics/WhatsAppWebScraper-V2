import Scripts
from Webdriver import Webdriver
from WhatsAppWebScraper import WhatsAppWebScraper

"""
Main isTyping application.
"""
def isTyping():


    driver = Webdriver()  # create new driver

    # Code for testing landing page
    # driver.getBrowser().get("http://localhost:63342/WhatsAppWebScraper/sample.html")
    # driver.getBrowser().execute_script(Scripts.initJQuery())
    # driver.getBrowser().execute_script(Scripts.getUserNameScript())

    scraper = WhatsAppWebScraper(driver)  # create new WhatsApp scraper
    scraper.scrape()  # scrape
    driver.close()  # close driver

    # loop for debugging
    while True:
        continue

isTyping()