from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty,
)
from itertools import (
    dropwhile,
    takewhile,
)
from re import compile
from requests import Session
from subprocess import check_output
from urllib.parse import quote_plus

from bs4 import BeautifulSoup


class BaseTie(metaclass=ABCMeta):

    @abstractproperty
    def PASSIVE(self):
        pass

    @abstractmethod
    def prepare(self, *args, **kwargs):
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        pass


class URLTie(BaseTie):

    @abstractproperty
    def DEFAULT_URL(self):
        pass

    url = None
    name = None
    document = None

    def __init__(self):
        self.session = Session()
        self.session.headers = {
            'User-Agent':  # Look like an XP douche
            'Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)'}  # trololo

    def prepare(self, name):
        self.name = name
        self.url = self.DEFAULT_URL.format(name=quote_plus(self.name))
        response = self.session.get(self.url)
        self.document = BeautifulSoup(response.content, 'html.parser')


class HeadTie(URLTie):
    DEFAULT_URL = "http://{}"
    PASSIVE = False

    response = None

    def prepare(self, name):
        self.url = self.DEFAULT_URL.format(name)
        self.response = self.session.head(self.url, allow_redirects=True)


class ServerTie(HeadTie):
    messages = {
        "hdr": "Server header: {}",
    }

    def print_header(self, response):
        print(self.messages['hdr'].format(response.headers.get('server')))

    def run(self):
        for response in self.response.history + [self.response, ]:
            self.print_header(response)


class ExecutiveTie(BaseTie):

    @abstractproperty
    def COMMAND(self):
        pass

    results = None

    def prepare(self, name):
        self.results = check_output((self.COMMAND, name)).decode()


class WhoisTie(ExecutiveTie):

    COMMAND = 'whois'
    PASSIVE = True

    def run(self):
        lines = "\n".join(takewhile(
            lambda x: not x.lower().startswith('>>>'),
            dropwhile(
                lambda x: not x.lower().startswith('domain name:'),
                self.results.splitlines())))
        print(lines)


class OninstagramTie(URLTie):

    DEFAULT_URL = "http://www.oninstagram.com/profile/search?query={name}"
    PASSIVE = True

    def run(self):
        emails = self.document.find_all('span', style="font-weight:bold;")
        for email in emails:
            print(email.get_text())


class LinkedinTie(URLTie):

    DEFAULT_URL = (
        "https://classic.startpage.com/do/search?&query="
        "site%3Alinkedin.com%2Fin+{name}")
    LINK_RE = compile(r"title_\d+")
    PASSIVE = True

    def run(self):
        names = self.document.find_all(id=self.LINK_RE)
        for name in names:
            title = name.get_text()
            if not title.endswith('LinkedIn'):
                continue
            url = name['href']
            print("{}: {}".format(title, url))
