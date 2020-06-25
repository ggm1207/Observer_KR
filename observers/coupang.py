import sys
from time import sleep

from selenium.common.exceptions import NoSuchElementException

sys.path.append('..')
from utils import tm2int, hangul2url
from base import BaseCralwer
from urls import COUPANG_LOGIN_URL, COUPANG_SEARCH_URL


class Coupang(BaseCralwer):
    def __init__(self): # init, login, delete alert
        super().__init__()
        self.log.info("COUPANG Observer Starting...")
        self.products = []

    def login(self):
        self.log.info("COUPANG Observer Login...")
        self.get(COUPANG_LOGIN_URL) 

        self.findE_id('login-email-input').send_keys(self.login_key['coupang']['id'])
        self.findE_id('login-password-input').send_keys(self.login_key['coupang']['pw'])
        self.findE_cn('login__button').click()

    def search_products(self, prod):
        self.log.info("COUPANG Observer Searching Products...")
        self.get(COUPANG_SEARCH_URL.format(hangul2url(prod['keyword'])))

        pages = 10
        self.links = []
        self.titles = []
        self.prices = []

        while pages:
            titles = self.findEs_cs("a > dl > dd > div > div.name")
            prices = self.findEs_cs("div.price > em > strong")
            links = self.findEs_cs("form > div > div > ul > li > a")
            for price, link, title in zip(prices, links, titles):
                price = tm2int(price.text)
                if price > prod['high_price']: continue
                if price < prod['low_price']: continue

                self.prices.append(price)
                self.titles.append(title.text)
                self.links.append(link.get_attribute("href"))

            # self.findE_cn("btn-next").click()
            self.findE_lt("다음").click()

            pages -= 1

    def check_products(self, prod):
        self.log.info("COUPANG Observer Checking Products...")
        datas = {
                'type': 'keyword',
                'name': 'Coupang',
                }

        idx = 0
        for link, title, price in zip(self.links, self.titles, self.prices):
            if not self.check_coupang_product(link):
                continue

            datas['link' + str(idx)] = link + '\n' + '{} {}\n'.format(title, price)
            idx += 1
        datas['lens'] = idx
        if idx:
            self.send_datas('http://127.0.0.1:5000/gateway', datas)

            

    def check_coupang_product(self, link):
        self.log.info("COUPANG Observer Checking Urls:{}".format(link))
        self.get(link)

        if self.findE_cn("prod-buy-btn") == "":
            return False
        return True
        
    def check_urls(self):
        pass

if __name__ == "__main__":
    a = Coupang() # test
    a.run()
