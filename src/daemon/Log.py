import sys
import enum

class LogLevel(enum.IntEnum):
    ddebug = 0
    debug = 1
    info = 2
    warning = 3
    error = 4

_loglevel = LogLevel.ddebug

def log(loglevel, content):
    if _loglevel <= loglevel:
        print(f"{loglevel.name}: {content}", file=sys.stderr)
