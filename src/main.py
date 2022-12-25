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
    errors = []
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(
            get_soup(
                session, urljoin(MAIN_DOC_URL, 'whatsnew/')
            ).select(
                '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
            )
    ):
        version_link = urljoin(
            urljoin(MAIN_DOC_URL, 'whatsnew/'),
            find_tag(section, 'a')['href']
        )

        try:
            soup = get_soup(session, version_link)
        except AttributeError as e:
            errors.append(e)
            continue
        results.append((version_link,
                        find_tag(soup, 'h1').text,
                        find_tag(soup, 'dl').text.replace('\n', ' ')))
    for error in errors:
        logging.error(error)
    return results


ERROR_VERSIONS = 'Ничего не нашлось'


def latest_versions(session):
    for ul in get_soup(
            session, MAIN_DOC_URL
    ).select('div.sphinxsidebarwrapper ul'):
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ValueError(ERROR_VERSIONS)
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
    pdf_a4_tag = get_soup(
        session, urljoin(MAIN_DOC_URL, 'download.html')
    ).select_one(
        'table.docutils a[href*="pdf-a4"][href$=".zip"]'
    )
    archive_url = urljoin(
        urljoin(MAIN_DOC_URL, 'download.html'), pdf_a4_tag['href']
    )
    DOWNLOADS_DIR = BASE_DIR / 'downloads'
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    archive_path = DOWNLOADS_DIR / archive_url.split('/')[-1]
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(LOG_DOWNLOADS.format(archive_path))


LOG_PEP = ('Несовпадающие статусы: \n'
           '{} \n'
           'Статус в карточке: {} \n'
           'Ожидаемые статусы: {}')


def pep(session):
    info_logs = []
    hrefs = {}
    for tag in get_soup(
            session, PEP_URL
    ).select('section#pep-content tr'):
        href = tag.find('a')
        abbr = tag.find('abbr')
        if href is not None and abbr is not None:
            hrefs[href['href']] = abbr.text[1:]
    status_count = defaultdict(int)
    for href, status in tqdm(set(hrefs.items())):
        tag_abbr = get_soup(
            session, urljoin(PEP_URL, href)
        ).select_one('dl abbr')
        if tag_abbr.text in EXPECTED_STATUS[status]:
            status_count[tag_abbr.text] += 1
        else:
            info_logs.append(LOG_PEP.format(
                urljoin(PEP_URL, href),
                tag_abbr.text,
                *EXPECTED_STATUS[status]
            ))
    for info in info_logs:
        logging.info(info)
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

START_LOG = 'Парсер запущен!'
ARGS_LOG = 'Аргументы командной строки: {}'
FINISH_LOG = 'Парсер завершил работу.'


def main():
    configure_logging()
    logging.info(START_LOG)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(ARGS_LOG.format(args))
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
    logging.info(FINISH_LOG)


if __name__ == '__main__':
    main()
