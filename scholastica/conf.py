import datetime
import os
import sys

home = os.path.expanduser("~")
MAIN_DIR = os.path.join(home, "scholastica")
GEDIT_DIR = os.path.join(MAIN_DIR, "gedit_plugin")
LOGS_DIR = os.path.join(GEDIT_DIR, "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
now = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
LOGS_FILE = os.path.join(LOGS_DIR, "log_" + now + ".txt")
LOG_FILTER = 0

