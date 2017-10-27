from dosbox import Server
import logging
logger = logging.getLogger("dosbox.gdbserver")


class GdbServer(Server):

    def start(self, host, port):
        logger.debug("start")

    def stop(self, host, port):
        logger.debug("stop")

currentServer = GdbServer()
