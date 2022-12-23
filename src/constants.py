from pathlib import Path

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
DOWNLOADS_DIR = BASE_DIR / 'downloads'
RESULTS_DIR = BASE_DIR / 'results'

LOG_FILE = LOG_DIR / 'parser.log'

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

CLI_ARGS = (
    'pretty',
    'file'
)

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

ERRORS_MESSAGE = {
    'get_response': 'Возникла ошибка при загрузке страницы {}',
    'find_tag': 'Не найден тег {} {}'
}

INFO_LOG = []
LOGS = {
    'download': 'Архив был загружен и сохранён: {}',

    'pep': 'Несовпадающие статусы: \n'
           '{} \n'
           'Статус в карточке: {} \n'
           'Ожидаемые статусы: {}'
}

