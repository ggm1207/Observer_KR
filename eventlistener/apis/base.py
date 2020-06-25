import os
import sys
import os.path as p

abs_dir = p.join(p.abspath(__file__), '..')
sys.path.append(p.join(abs_dir, '..', '..'))
from utils import parsingFile

class BaseApi:
    def __init__(self, name):
        self.api_login = parsingFile(p.abspath(p.join(abs_dir, '..', '..', 'config', 'api')))
        self.isLogin = False
        if self.api_login[name]['use']:
            self.login()
            self.isLogin = True

    def login(self):
        raise NotImplementedError

    def parsing(self, datas):
        if self.isLogin:
            if datas['type'] == 'keyword':
                self._parsing_keyword(datas)
            else:
                self._parsing_url(datas)

    def _parsing_keyword(self):
        raise NotImplementedError
    
    def _parsing_url(self):
        raise NotImplementedError
