class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    def __init__(self, error_message):
        self.error_message = error_message

