from bs4 import BeautifulSoup
from requests import RequestException

from exception import ParserFindTagException
from constants import ERRORS_MESSAGE


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        raise RequestException(ERRORS_MESSAGE['get_response'].format(url))


def get_soup(response):
    return BeautifulSoup(response.text, features='lxml')


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(ERRORS_MESSAGE['find_tag'].format(tag, attrs))
    return searched_tag

