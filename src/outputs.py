import csv
import datetime as dt
import logging
from prettytable import PrettyTable

from constants import DATETIME_FORMAT, BASE_DIR


def default_output(*results):
    for row in results[0]:
        print(*row)


def pretty_output(*results):
    table = PrettyTable()
    table.field_names = results[0][0]
    table.align = 'l'
    table.add_rows(results[0][1:])
    print(table)


def file_output(results, cli_args):
    RESULTS_DIR = BASE_DIR / 'results'
    RESULTS_DIR.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = RESULTS_DIR / file_name

    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)

    logging.info(f'Файл с результатами был сохранён: {file_path}')


CLI_ARGS_DEF = {
    'pretty': pretty_output,
    'file': file_output,
    None: default_output
}


def control_output(results, cli_args):
    output = cli_args.output
    CLI_ARGS_DEF[output](results, cli_args)
