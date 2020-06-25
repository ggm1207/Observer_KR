import os
import sys
import smtplib
from email.mime.text import MIMEText

abs_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(abs_dir, '..', '..'))

from .base import BaseApi
from utils import parsingFile

class Gmail(BaseApi):
    def __init__(self):
        super().__init__("google")
        print('Gmail Init')
        self.msg_keyword = "Observer: {}\nProduct Num: {}\n"

    def login(self):
        self.GMAIL_ID = self.api_login['google']['id']
        self.GMAIL_PWD = self.api_login['google']['pw']

        try:
            self.smtp = smtplib.SMTP('smtp.gmail.com', 587)
            self.smtp.ehlo()
            self.smtp.starttls()
            self.smtp.login(self.GMAIL_ID, self.GMAIL_PWD)
        except:
            self.__del__()

    def _parsing_keyword(self, datas):
        msg = ""
        for link, products in datas['links'].items():
            msg  += '*' * 30 + '\n'
            msg  += 'Link:{}\n'.format(link)
            for title, price in products.items():
                msg  += '{} {}\n'.format(title, price)
            msg += '\n'

        self.msg_keyword = self.msg_keyword.format(datas['name'], datas['lens'])
        self.msg_keyword += msg

        self.send_gmail(self.msg_keyword)

    def _parsing_url(self, datas):
        pass

    def send_gmail(self, msg):
        email = self.GMAIL_ID + "@gmail.com"
        mimetext = MIMEText(msg)
        mimetext['Subject'] = "Observer Notification"
        mimetext['To'] = email
        self.smtp.sendmail(email, "ticonhi@naver.com", mimetext.as_string())

        self.smtp.quit()

