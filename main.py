from Webdriver import Webdriver
from WhatsAppWebScraper import WhatsAppWebScraper

"""
Main isTyping application.
"""
def isTyping():

    driver = Webdriver()  # create new driver
    scraper = WhatsAppWebScraper(driver)  # create new WhatsApp scraper
    scraper.scrape()  # scrape
    driver.close()  # close driver

isTyping()