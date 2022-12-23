from requests import RequestException
from exception import ParserFindTagException
from bs4 import BeautifulSoup
import logging


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def get_soup(response):
    return BeautifulSoup(response.text, features='lxml')


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_message = f'Не найден тег {tag} {attrs}'
        raise ParserFindTagException(error_message)
    return searched_tag
