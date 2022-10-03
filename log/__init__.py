"""Script Logger

At the import stage creates a shared logging instance with a
NullHandler type. Using the attributes and methods of the
instance, you can change the Handler type, log message format,
etc.

.USAGE

import log
from log import logger

# `filelogger` object definition
logger.loggerName = "syslog"
logger.logFileName = "system.log"
logger.set_filelogger()

# set log level to `INFO`
logger.set_level("info")

# `stream logger` object definition
logger.set_streamlogger()

# logging
logger.set_format("main")
logger.info("Informational message")
logger.critical("Critical message")

"""
__version__ = "0.2.3"
## Import logger
from .logger import Logger

__all__ = ["Logger"]


def createLogger(timeFormat: int = 24, loggerName: str = ""):
    baseLogger = Logger()

    return baseLogger


# Creating base (null) logger instance
logger = createLogger()
