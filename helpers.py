"""
Helper functions for logging.
https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
"""
import logging
import logging.handlers
from preprocessing import settings


def listener_configurer():
    """

    :return:
    """
    root = logging.getLogger()
    output_file = str(settings.raw_path.parent.joinpath(f'preprocessing_{settings.project}.log'))
    h = logging.handlers.RotatingFileHandler(output_file)  # , 'a', 300, 10)  # 'a', 300, 10 ?
    f = logging.Formatter('%(levelname)s | %(name)s | %(message)s')
    h.setFormatter(f)
    root.addHandler(h)
    root.setLevel(logging.WARNING)


def listener_process(queue, configurer):  # ???
    """

    :param queue:
    :param configurer:
    :return:
    """
    configurer()
    while True:
        try:
            record = queue.get()
            if record is None:
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except Exception:
            import sys, traceback
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def worker_configurer(queue):
    """

    :param queue:
    :return:
    """
    h = logging.handlers.QueueHandler(queue)  # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.WARNING)