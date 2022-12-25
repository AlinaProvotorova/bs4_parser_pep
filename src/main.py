import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import MAIN_DOC_URL, PEP_URL, EXPECTED_STATUS, BASE_DIR
from outputs import control_output
from utils import find_tag, get_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response, soup = get_soup(session, version_link)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ValueError('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        re_search = re.search(pattern, a_tag.text)
        if re_search is not None:
            version, status = re_search.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


LOG_DOWNLOADS = 'Архив был загружен и сохранён: {}'


def download(session):
    soup = get_soup(session, urljoin(MAIN_DOC_URL, 'download.html'))
    table_tag = find_tag(
        soup,
        'table',
        {'class': 'docutils'}
    )
    pdf_a4_tag = find_tag(table_tag, 'a',
                          {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(urljoin(MAIN_DOC_URL, 'download.html'), pdf_a4_link)
    filename = archive_url.split('/')[-1]
    DOWNLOADS_DIR = BASE_DIR / 'downloads'
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    archive_path = DOWNLOADS_DIR / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(LOG_DOWNLOADS.format(archive_path))


LOG_PEP = ('Несовпадающие статусы: \n'
           '{} \n'
           'Статус в карточке: {} \n'
           'Ожидаемые статусы: {}')


def pep(session):
    info = []
    soup = get_soup(session, PEP_URL)
    pep_content = find_tag(soup, 'section', {'id': 'pep-content'})
    tr_tags = pep_content.find_all('tr')
    hrefs = {}
    for tag in tr_tags:
        href = tag.find('a')
        abbr = tag.find('abbr')
        if href is not None and abbr is not None:
            hrefs[href['href']] = abbr.text[1:]
    status_count = defaultdict(int)
    for href, status in tqdm(set(hrefs.items())):
        soup = get_soup(session, urljoin(PEP_URL, href))
        dl_tag = find_tag(soup, 'dl')
        tag_abbr = find_tag(dl_tag, 'abbr')
        if tag_abbr.text in EXPECTED_STATUS[status]:
            status_count[tag_abbr.text] += 1
        else:
            info.append(LOG_PEP.format(
                urljoin(PEP_URL, href),
                tag_abbr.text,
                *EXPECTED_STATUS[status]
            ))
    for i in info:
        logging.info(i)
    return [
        ('Статус', 'Количество'),
        *status_count.items(),
        ('Total', sum(status_count.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}

ERROR = ('Программа завершилась по причине: \n'
         '{}')


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as e:
        logging.exception(ERROR.format(e))
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
