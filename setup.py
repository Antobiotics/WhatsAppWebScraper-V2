try:
    from setuptools import setup
except:
    from distutils.core import setup

try:
    import multiprocessing
except ImportError:
    pass

setup(
    name="whatsapp-scraper",
    version='1.0.0',
    description="WhatsApp data scraping with Selenium",
    author_email="albclus@gmail.com",
    url="https://github.com/Antobiotics/whatsapp-scraper",
    platforms="Posix; MacOS X; Windows",
    entry_points = {
        "console_scripts": ['whatsapp_scraper = whatsapp_scraper.main:main']
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
    ],
    packages=[
        "whatsapp_scraper"
    ],
    install_requires=[
        "click",
        "coloredlogs",
        "selenium"
    ]
)

