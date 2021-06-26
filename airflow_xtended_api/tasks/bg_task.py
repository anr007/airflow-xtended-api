from threading import Thread
import signal
import sys
import os
import logging


class BackgroundTask(Thread):
    @staticmethod
    def sigterm_receiver(signal_num, stack_frame):
        logging.info("Signal Received: SIGTERM")
        sys.exit()

    @staticmethod
    def sigabrt_receiver(signal_num, stack_frame):
        logging.info("Signal Received: SIGKILL")

    @staticmethod
    def sigint_receiver(signal_num, stack_frame):
        logging.info("Signal Received: SIGINT")

    @staticmethod
    def sigquit_receiver(signal_num, stack_frame):
        logging.info("Signal Received: SIGQUIT")

    def __init__(self):
        # Call the Thread class's init function
        Thread.__init__(self)
        logging.info("Running Background Task as: " + str(os.getpid()))
        signal.signal(signal.SIGTERM, self.sigterm_receiver)
        signal.signal(signal.SIGABRT, self.sigabrt_receiver)
        signal.signal(signal.SIGINT, self.sigint_receiver)
        signal.signal(signal.SIGQUIT, self.sigquit_receiver)

    def run(self):
        # To be implemented by child class
        pass
