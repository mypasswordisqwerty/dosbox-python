import logging


class Logger(object):
    """ Logger plugin base """

    def __init__(self, loggerName=None):
        loggerName = loggerName or self.__class__.__name__
        self.logger = logging.getLogger("dosbox."+loggerName)
        self._fileh = None

    def setLogFile(self, filename=None):
        if self._fileh:
            self.logger.removeHandler(self._fileh)
        self._fileh = None
        if filename:
            self._fileh = logging.FileHandler(filename)
            self.logger.addHandler(self._fileh)

    def debug(self, log, *args):
        self.logger.debug(log, *args)

    def log(self, log, *args):
        self.logger.info(log, *args)
