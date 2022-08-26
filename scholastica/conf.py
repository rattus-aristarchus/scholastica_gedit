import datetime
import io
import os
import sys
import cProfile
import pstats
import logging

home = os.path.expanduser("~")
MAIN_DIR = os.path.join(home, "scholastica")
GEDIT_DIR = os.path.join(MAIN_DIR, "gedit_plugin")
LOGS_DIR = os.path.join(GEDIT_DIR, "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
now = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
LOGS_FILE = os.path.join(LOGS_DIR, "log_" + now + ".txt")
PROFILE_DUMP = os.path.join(LOGS_DIR, "profile_dump.txt")
LOG_FILTER = 0

logging.basicConfig(filename=LOGS_FILE,
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

profile = cProfile.Profile()


def start_profiling():
    logger.info("start_profiling")
    profile.enable()


def end_profiling():
    logger.info("end_profiling")
    profile.disable()
    logger.debug("0")
    result = io.StringIO()
    logger.debug("1")
    stats = pstats.Stats(profile, stream=result)
    stats.sort_stats('cumulative').print_stats()
    """
    logger.debug("2")
    stats = stats.strip_dirs()
    logger.debug("3")
    stats = stats.sort_stats(SortKey.CUMULATIVE)
    logger.debug("4")
    stats = stats.print_stats()
    logger.debug("5")
    """
    if os.path.exists(PROFILE_DUMP):
        os.remove(PROFILE_DUMP)
    with open(PROFILE_DUMP, "w+") as file:
        file.write(result.getvalue())
        