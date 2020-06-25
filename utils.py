import logging
from urllib import parse
from collections import defaultdict


from rich.logging import RichHandler
from rich.traceback import install

install()

FORMAT = "%(message)s"
logging.basicConfig(
        level=logging.INFO, format=FORMAT, datefmt="[%Y-%m-%d %X]",
        handlers=[RichHandler()]
        )

log = logging.getLogger("rich")

def getLogger():
    global log
    return log


def parsingFile(fpath):
    parser = {}
    dup_check = defaultdict(int)

    for line in open(fpath, 'r'):
        line = line.rstrip('\n')
        if line == '': continue
        if line.startswith('['):
            section = line[1:-1]
            if section == 'product':
                dup_check[section] += 1
                section = section + str(dup_check[section])
            parser[section] = {}
            continue
        if line.startswith('#'):
            continue
        key, value = line.split('=') 
        parser[section][key] = int(value) if value.isdecimal() else value
    return parser

def grouped(iterable, n):
    return zip(*[iter(iterable)]*n)

def tm2int(text):
    return int(text.replace(',',''))

def hangul2url(text):
    return parse.quote(text)


if __name__ == "__main__":
    print(parsingFile('./config/product'))
    print(parsingFile('./config/login'))

