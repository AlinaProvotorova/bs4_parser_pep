import re
from urllib.parse import urljoin
from collections import defaultdict

import logging
import requests_cache
from tqdm import tqdm

from constants import MAIN_DOC_URL, PEP_URL, EXPECTED_STATUS, DOWNLOADS_DIR, INFO
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag, get_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    soup = get_soup(response)

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
        response = get_response(session, version_link)
        soup = get_soup(response)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )

    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)

    soup = get_soup(response)

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


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)

    soup = get_soup(response)

    table_tag = find_tag(soup, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, 'a',
                          {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]

    DOWNLOADS_DIR.mkdir(exist_ok=True)
    archive_path = DOWNLOADS_DIR / filename

    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    info = []
    response = get_response(session, PEP_URL)
    soup = get_soup(response)
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
        response = get_response(session, urljoin(PEP_URL, href))

        soup = get_soup(response)
        dl_tag = find_tag(soup, 'dl')
        tag_abbr = find_tag(dl_tag, 'abbr')

        if tag_abbr.text in EXPECTED_STATUS[status]:
            status_count[tag_abbr.text] += 1
        else:
            info.append((urljoin(PEP_URL, href), tag_abbr.text, EXPECTED_STATUS[status]))
            # info = f'Несовпадающие статусы: \n' \
            #        f'{urljoin(PEP_URL, href)} \n' \
            #        f'Статус в карточке: {tag_abbr.text} \n' \
            #        f'Ожидаемые статусы: {EXPECTED_STATUS[status]}'

    # logging.info(INFO)

    return [
        ('Статус', 'Количество'),
        *status_count.items(),
        ('Total', sum(status_count.values())),
    ], info


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


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

        results, info = MODE_TO_FUNCTION[parser_mode](session)

        if results is not None:
            control_output(results, args)

    except Exception as e:
        logging.info(e, stack_info=True)

    logging.info('Парсер завершил работу.')
    # logging.info(INFO)

if __name__ == '__main__':
    main()
