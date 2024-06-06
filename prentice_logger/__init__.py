import logging
import sys

# Credit to @KetanSovanshi
class CustomExtraLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        my_context = kwargs.pop('extra', self.extra['extra'])
        return '[%s] %s' % (my_context, msg), kwargs


def get_logger(name, level=logging.DEBUG) -> logging.Logger:
    """"
    Logging to logfile and console
    """
    FORMAT = "[%(levelname)s  %(name)s %(module)s:%(lineno)s - %(funcName)s() - %(asctime)s]\n\t %(message)s \n"
    TIME_FORMAT = "%d.%m.%Y %I:%M:%S %p"
    FILENAME = './log.log'

    # Set up basic file logging
    logging.basicConfig(format=FORMAT, datefmt=TIME_FORMAT, level=level, filename=FILENAME)

    # Create a logger instance
    logger_instance = logging.getLogger(name)

    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Add the same formatter to the console handler
    console_handler.setFormatter(logging.Formatter(fmt=FORMAT, datefmt=TIME_FORMAT))
    
    # Add the console handler to the logger
    logger_instance.addHandler(console_handler)

    return logger_instance


logger = get_logger(__name__)

logger.info('Logger initiated')