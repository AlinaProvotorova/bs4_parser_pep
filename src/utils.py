from bs4 import BeautifulSoup
from requests import RequestException

from exception import ParserFindTagException

ERRORS_MESSAGE_RESPONSE = 'Возникла ошибка при загрузке страницы {}'


def get_soup(session, url):
    return BeautifulSoup(get_response(session, url).text, features='lxml')


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        raise AttributeError(ERRORS_MESSAGE_RESPONSE.format(url))


ERRORS_MESSAGE_TAG = 'Не найден тег {} {}'


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=({} if attrs is None else attrs))
    if searched_tag is None:
        raise ParserFindTagException(
            ERRORS_MESSAGE_TAG.format(tag, attrs)
        )
    return searched_tag
