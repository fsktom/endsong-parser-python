class WrongDate(Exception):
    """Used by time_utils.convert_to_unix() if the provided date (user input)
    is not in "YYYY.MM.DD-hh.mm.ss" format
    """
