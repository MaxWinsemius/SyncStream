import os
import stat

from config import _runfolder
from models import (
    Interface,
)


def _is_socket(path):
    # Checks if path is a socket or not
    return stat.S_ISSOCK(os.stat(path).st_mode)


def get_interfaces() -> list[Interface]:
    # Gets all sockets in rundir
    return [
        Interface.model_validate({'name': p}) for p in os.listdir(_runfolder)
        if _is_socket(f"{_runfolder}/{p}")
    ]
