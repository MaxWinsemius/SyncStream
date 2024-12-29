import os
import time
import random
import json

from config import (
    _runfolder,
    _lockfile,
    datafile
)

haslock = False

if not os.path.isdir(_runfolder):
    raise Exception(f"Run folder {_runfolder} doesn't exist, did you boot?")


def _pid():
    return os.getpid()


def _randsleep():
    time.sleep(random.randint(10, 100) / 100)


def get_lock():
    if os.path.isfile(_lockfile):
        with open(_lockfile, "r") as f:
            if f.read() != '':
                print(f"Can't get lock on {_lockfile}, it already exists. " +
                      "If this keeps on " +
                      "happening ensure that no other manage command is " +
                      "hanging / accidentally crashed")
                _randsleep()

                # return to prevent recursion
                return get_lock()

    with open(_lockfile, "w") as f:
        f.write((str)(_pid()))

    _randsleep()

    if not os.path.isfile(_lockfile):
        print(f"Can't get lock on {_lockfile}, it was removed after writing" +
              "my PID to it. If this " +
              "keeps on happening ensure that no other manage command is " +
              "hanging / accidentally crashed")
        return get_lock()

    with open(_lockfile, "r") as f:
        file_pid = f.read()
        if (int)(file_pid) != (int)(_pid()):
            print(f"Can't get lock on {_lockfile}, it was replaced by " +
                  "another process. If this " +
                  "keeps on happening ensure that no other manage command is" +
                  " hanging / accidentally crashed")
            return get_lock()

    # lockfile ensured after OS threading.
    global haslock
    haslock = True
    return haslock


def release_lock(istry=False):
    def rprint(msg):
        if not istry:
            print(msg)
        return

    global haslock
    haslock = False

    if not os.path.isfile(_lockfile):
        return rprint(f"Lockfile {_lockfile} doesn't" +
                      "exist! Did something delete it?")

    with open(_lockfile, "r") as f:
        file_pid = f.read()
        if file_pid != '' and (int)(file_pid) != (int)(_pid()):
            return rprint(f"Lockfile {_lockfile} didn't contain my PID?!")

    os.remove(_lockfile)


def try_release_lock():
    release_lock(True)


def get_running_json():
    if not os.path.isfile(datafile):
        return []

    with open(datafile) as f:
        return json.load(f)


def write_running_json(data):
    with open(datafile, 'w') as f:
        json.dump(data, f)
