import csv
import datetime as dt
import logging
from prettytable import PrettyTable

from constants import DATETIME_FORMAT, BASE_DIR, PRETTY, FILE


def default_output(results, *cli_args):
    for row in results:
        print(*row)


def pretty_output(results, *cli_args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


INFO_OUTPUT = 'Файл с результатами был сохранён: {}'


def file_output(results, cli_args):
    RESULTS_DIR = BASE_DIR / 'results'
    RESULTS_DIR.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = RESULTS_DIR / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        writer.writerows(results)
    logging.info(INFO_OUTPUT.format(file_path))


CLI_ARGS_DEF = {
    PRETTY: pretty_output,
    FILE: file_output,
    None: default_output
}


def control_output(results, cli_args):
    CLI_ARGS_DEF[cli_args.output](results, cli_args)
