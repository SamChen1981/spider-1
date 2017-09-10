# encoding=utf8
from selenium import webdriver


class SeleniumClient(object):

    @classmethod
    def get_driver(cls):
        driver = webdriver.PhantomJS()
        return driver


class HttpClient(object):
    """HTTP访问后端，使用selenium+phantomjs
    """
    def request(self, url):
        driver.get(url)
        html = driver.page_source
        return {"text": html}

driver = SeleniumClient().get_driver()
