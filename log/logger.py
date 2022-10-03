"""Script logging configuration and management

The `Logger` class allows you to create a logging instance, with
a NullHandler by default. After creating an instance by changing
attributes and using class methods, you can change the default
Handler to StreamHandler or FileHandler.
Class methods also allow you to change the log message format and
logging level.

Class Init Parameters
---------------------

timeFormat: int
    Time format. 12 or 24 hours (default) time format
loggerName: str
    Name of the logging instance
"""
import sys
import logging


class Logger:
    """Custom logging based on `logging` standart module

    Attributes
    ----------

    loggerName : str
        logging instance name
    logFileName : str
        full path to log file
    logLevel : int
        log level
    logDateFormat : str
        log date-time format
    logHandler : object
        log handler type: Null (default), File, Stream

    Methods
    -------

    set_basic()
        Force set log basic stream logger definition
    set_filelogger(fileMode)
        Log FileHandler definition
    set_streamlogger()
        Log StreamHandler definition
    set_level(logLevel)
        Sets log level
    set_format(logFormatter)
        Change log Formatter settings
    critical(logMessage)
        Logging `CRITICAL` message
    error(logMessage)
        Logging `ERROR` message
    warning(logMessage)
        Logging `WARNING` message
    info(logMessage)
        Logging `INFO` message
    debug(logMessage)
        Logging `DEBUG` message
    exception(logMessage)
        Logging `ERROR` message raised from Exception
    shutdown
        Stop logging and closing log Handler
    """

    def __init__(self, timeFormat: int = 24, loggerName: str = "log"):
        """Main parameters init"""
        self.loggerName = loggerName
        self.logFileName = "script.log"
        self.logLevel = logging.DEBUG

        timeFormats = {12: "%Y-%m-%d %I:%M:%S %p %z", 24: "%Y-%m-%d %H:%M:%S %z"}
        if timeFormat == 12 or timeFormat == 24:
            self.logDateFormat = timeFormats.get(timeFormat, "%Y-%m-%d %H:%M:%S %z")
        else:
            # Default 24h time format
            self.logDateFormat = "%Y-%m-%d %H:%M:%S %z"

        # self.logCustomLevels = {}
        self.logPredefinedLevels = {
            "critical": 50,
            "error": 40,
            "warning": 30,
            "info": 20,
            "debug": 10,
            "notset": 0,
        }

        """Log null handler definition"""
        self.logHandler = logging.NullHandler()

        ## Creating `logger` object
        #
        # self.log = logging.getLogger(__name__)
        self.log = logging.getLogger(self.loggerName)
        self.log.addHandler(self.logHandler)
        self.log.setLevel(self.logLevel)

    @property
    def set_basic(self):
        """Force set log basic stream logger definition"""
        self.log.removeHandler(self.logHandler)

        logging.basicConfig(
            force=True,
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
            encoding="utf-8",
        )

    def set_filelogger(self, fileMode: str = "w"):
        """Log file handler definition

        Parameters
        ----------

        fileMode : str
            log file mode:
            "a" - append to existing log file
            "w" - replace existing file (default)
        """
        self.log.removeHandler(self.logHandler)

        self.logHandler = logging.FileHandler(
            self.logFileName, mode=fileMode, encoding="utf-8"
        )

        ## Change handler to `FileHandler`
        self.log = logging.getLogger(self.loggerName)
        self.log.addHandler(self.logHandler)

    def set_streamlogger(self):
        """Log stream handler definition"""
        self.log.removeHandler(self.logHandler)

        self.logHandler = logging.StreamHandler()
        # self.logHandler.setStream(sys.stdout)

        ## Change handler to `StreamHandler`
        self.log = logging.getLogger(self.loggerName)
        self.log.addHandler(self.logHandler)

    def set_level(self, logLevel: str = "debug"):
        """Set log level

        Parameters
        ----------

        logLevel : str
            log level string value. Default "debug"
        """
        if logLevel:
            self.logLevel = self.logPredefinedLevels.get(
                logLevel.lower(), logging.DEBUG
            )
        else:
            self.logLevel = logLevel

        self.log.setLevel(self.logLevel)

    def set_format(self, logFormatter: str = "base"):
        """
        Log Formatter settings

        Parameters
        ----------

        logFormatter : str
            log message formatter type. Available predefined formatters:

            "base"    - simple log message format, message only
            "default" - default formater. Incl. fields: `datetime` (default
                        datetime format), `log level name` (string), `logger
                        name`, `PID` and `message`
            "main"    - customized default formater. Extended `datetime`
                        field format. Sets the date and time in 12 or 24
                        (default) hour format from a class level variable
        """
        logFormatters = {
            "base": logging.Formatter("%(message)s"),
            "default": logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s[%(process)d]: %(message)s",
            ),
            "main": logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s[%(process)d]: %(message)s",
                datefmt=self.logDateFormat,
            ),
        }
        self.logFormatter = logFormatters.get(
            logFormatter, logging.Formatter("%(message)s")
        )

        # Set log handler formatter
        self.logHandler.setFormatter(self.logFormatter)

    @property
    def shutdown(self):
        """Closing handler and shutdown logging"""
        self.logHandler.close()

    """Log message logging by level

    Parameters
    ----------
    logMessage : str
        log message
    """

    def critical(self, logMessage: str):
        """CRITICAL"""
        self.log.critical(logMessage)

    def error(self, logMessage: str):
        """ERROR"""
        self.log.error(logMessage)

    def warning(self, logMessage: str):
        """WARNING"""
        self.log.warning(logMessage)

    def info(self, logMessage: str):
        """INFO"""
        self.log.info(logMessage)

    def debug(self, logMessage: str):
        """DEBUG"""
        self.log.debug(logMessage)

    def exception(self, logMessage: str):
        """Logs a message with level ERROR on the root logger. To
        call from an exception handlers. Exception info is added
        to the logging message.
        """
        self.log.exception(logMessage)

    def notset(self, logLevel: str, logMessage: str):
        """Log Level
        Logs a message with level `logLevel` on the root logger.

        Parameters
        ----------

        logLevel : str
            the logging level (string) like "DEBUG", "ERROR",
            "INFO" etc.
        logMessage : str
            log message
        """
        self.log.log(logLevel.upper(), logMessage)


class FileLogger(Logger):
    """File logging"""

    pass
