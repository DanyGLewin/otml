import atexit
import logging
import os

from src.otml_configuration import settings

def setup_logger(verbose, very_verbose):
    if very_verbose:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    if os.path.exists(settings.logs_file):
        os.remove(settings.logs_file)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=settings.logs_file,
        filemode="a",
    )
    atexit.register(clean_logger)


def clean_logger():
    if os.path.getsize(settings.logs_file) == 0:
        os.remove(settings.logs_file)

