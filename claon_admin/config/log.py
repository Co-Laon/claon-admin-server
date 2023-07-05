import logging

try:
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
except Exception:
    ...

logger = logging.getLogger(__name__)
