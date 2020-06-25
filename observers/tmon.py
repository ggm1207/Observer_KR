import sys

from selenium.common.exceptions import NoSuchElementException

sys.path.append('..')
from utils import tm2int, hangul2url
from base import BaseCralwer, tryfindelements
from urls import TMON_LOGIN_URL, TMON_SEARCH_URL

class Tmon(BaseCralwer):
    def __init__(self): # init, login, delete alert
        super().__init__()
        self.log.info("TMON Observer Starting...")
        self.links = []

    def login(self):
        self.log.info("TMON Observer Login...")
        key = self.login_key['tmon']
        self.get(TMON_LOGIN_URL)
        self.findE_id('userid').send_keys(key['id'])
        self.findE_id('pwd').send_keys(key['pw'])
        self.findE_lt('로그인').click()
        self.get('http://search.tmon.co.kr') 

        # 오늘 하루 보지 않기, 1번 클릭하면 모든 팝업 다 지워짐
        expires = None
        try:
            expires = self.findE_cn("expires")
            expires.click()
        except:
            self.log.info("TMON Observer doesn't click expires.")


    def search_products(self, prod):
        self.log.info("TMON Observer Searching Products...")

        scrolls = 0
        self.get(TMON_SEARCH_URL.format(hangul2url(prod['keyword'])))

        self.scrollsTo(200000)

        self.links = [] # flush

        links = self.findEs_cs('section > div > ul > div > div > li > a')
        prices = self.findEs_cs('span.price > span.sale > i')
        low_limit = prod['low_price'] // 2
            
        for link, price in zip(links, prices):
            price = tm2int(price.text)

            # 상품의 최소 가격이 제시값을 넘는 경우
            if price > prod['high_price']:
                continue
            
            # 상품의 최소 가격이 너무 낮은 경우: 안에 있는 상품들이 사용자의 요구를 충족하지 못할거라고 가정
            if price < low_limit:
                continue
            self.links.append(link.get_attribute('href'))

    def check_products(self, prod):
        self.log.info("TMON Observer Checking Products...")
        datas = {
                'type': 'keyword',
                'name': 'Tmon'
                }
        idx = 0
        for link in self.links:
            sub_titles, sub_prices = self.check_tmon_product(link, prod)
            if not sub_titles:
                continue
            datas['link' + str(idx)] = link + '\n' + \
                    '\n'.join([title + '\n' +  str(price) for title, price in zip(sub_titles, sub_prices)])
            idx += 1
        datas['lens'] = idx

        if idx:
            self.send_datas('http://127.0.0.1:5000/gateway', datas)

    def check_tmon_product(self, link, prod):
        self.log.info("TMON Observer Checking Urls:{}".format(link))

        self.get(link)

        o_cssSelector = '#_optionScroll > div > div > div > div.dep-sel.dep{} > ul > li'
        options = self.findEs_cn("dep-sel")
        o_len = len(options) // 2

        if o_len == 0:
            product = self.findE_cs("ul.prod > li > span.tit").text
            price = self.findE_cs("div.price_area > div > div > span > strong").text
            price = tm2int(price)
            if prod['low_price'] <= price <= prod['high_price']:
                return [product], [price] 
            return [], []

        o_cIdx = 0
        o_sList = [0 for _ in range(o_len)]
        options = options[:o_len]
        o_maxList = [len(self.findEs_cs(o_cssSelector.format(0)))//2]

        # start
        options[0].click()

        products, prices = [], []

        while True:
            # product choiced
            if o_cIdx == o_len:
                product_price, product_title = None, None
                
                while not (product_price and product_title):
                    try:
                        product_price = self.findE_cs('div.price_area > div > div > span > strong')
                        product_title = self.findE_xp('//*[@id="_optionScroll"]/div/ul[1]/li/span[1]')
                        product_price = tm2int(product_price.text) 
                    except NoSuchElementException:
                        self.log.warning("NoSuchElementException:product_price,product_title")
                        last_option = None
                        while not last_option:
                            try:
                                options[o_cIdx-1].click()
                                last_option = self.findEs_cs(o_cssSelector.format( \
                                    o_cIdx-1))[o_sList[o_cIdx-1]-1]
                                last_option.click()
                            except NoSuchElementException:
                                self.log.warning("NoSuchElementException:last_option")
                if prod['low_price'] <= product_price <= prod['high_price']:
                    products.append(product_title.text)
                    prices.append(product_price)

                o_cIdx -= 1
                self.findE_cn("del").click()
                options[o_cIdx].click()
                continue
            
            # option add maxlen
            if o_sList[o_cIdx] == 0 and o_cIdx != 0:
                o_maxList.append(len(self.findEs_cs(o_cssSelector.format(o_cIdx)))//2)
                
            # option arrived maxlen
            if o_sList[o_cIdx] == o_maxList[o_cIdx]:
                o_sList[o_cIdx] = 0
                o_cIdx -= 1
                options[o_cIdx].click()
                o_maxList.pop()
                if o_maxList:
                    continue
                break
                    
            with tryfindelements(self.findEs_cs, o_cssSelector.format(o_cIdx)) as n_option:
                n_option = n_option[o_sList[o_cIdx]] 
                o_sList[o_cIdx] += 1  # option:n plus

                if n_option.get_attribute("class") == "soldout":
                    continue
                n_option.click()
                o_cIdx += 1  # options: n to n+1

        return products, prices
    
        
    def check_urls(self):
        pass
        

if __name__ == "__main__":
    a = Tmon()
    a.run()
