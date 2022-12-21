# Проект парсинга pep

Парсер данныx документации Python.

После клонирования репозитория итоговая структура проекта должна быть такой:
 
```
bs4_parser_pep
 ├── src/
     ├── __init__.py
     ├── configs.py
     ├── constants.py
     ├── exceptions.py
     ├── main.py
     ├── outputs.py
     └── utils.py
 ├── tests/
 ├── .flake8
 ├── .gitignore
 ├── README.md
 ├── pytest.ini
 └── requirements.txt  # Переносить из своего проекта не нужно.

```

#### Для получения ссылок на статьи нововведений 
в терминале введите команду:

```
(venv) ...\src$ python main.py whats-new --output pretty
```
или для сохранения в файл csv:
```
(venv) ...\src$ python main.py whats-new --output file
```

#### Для получения ссылок на документацию 
в терминале введите команду:

```
(venv) ...\src$ python main.py latest-versions --output pretty
```
или для сохранения в файл csv:
```
(venv) ...\src$ python main.py latest-versions --output file
```

#### Для получения информации PEP 
в терминале введите команду:

```
(venv) ...\src$ python main.py pep --output pretty
```
или для сохранения в файл csv:
```
(venv) ...\src$ python main.py pep --output file
```