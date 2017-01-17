import click

import whatsapp_scraper.logger as l

@click.group()
def main(**kwargs):
    l.INFO("Starting WhatsApp Scraper")

if __name__ == '__main__':
    main()
