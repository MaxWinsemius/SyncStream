import os
import sys
import time
import yaml
import tempfile
from subprocess import Popen

from models import (
    Interface,
    Animation,
    Running,
)

from state import (
    _runfolder,
    get_running_json as _get_running_json,
    write_running_json as _write_running_json,
)

from interface import get_interfaces


validated_animations: list[Animation] = None


def _get_running() -> list[Running]:
    return [Running.model_validate(r) for r in _get_running_json()]


def _write_running(running: list[Running]):
    _write_running_json([r.model_dump() for r in running])


def _get_animations() -> list[Animation]:
    global validated_animations

    # Cache!
    if validated_animations is not None:
        return validated_animations

    validated_animations = []

    all_files = os.listdir("../animations")
    all_animations = [
        a.rstrip('.py') for a in all_files if a.endswith(".py")
    ]

    for ani in all_animations:
        if f"{ani}.yaml" in all_files:
            validated_animations.append(Animation.model_validate({
                'name': ani,
            }))
        else:
            print(f"{ani} not have an animation configuration file, please " +
                  "make one!")

    return validated_animations


def _convert_options(options: list[str]) -> dict:
    data = {}
    for option in options:
        key, val = option.split("=")
        if val.isdigit():
            val = int(val)
        if isinstance(val, str) and ',' in val:
            val = [v if not v.isdigit() else int(v) for v in val.split(',')]
        data[key] = val
    return {'parameters': data}


def _merge_parameters(base: dict, overlay: dict) -> dict:
    return {**base, 'parameters': {
        **base['parameters'], **overlay['parameters']
    }}


def start(name: str, interfaces: list[str], options=list[str]):
    print(f"Starting animation '{name}' on interfaces " +
          f"'{interfaces}' with options: {options}")

    if options is None:
        options = {}
    else:
        options = _convert_options(options)

    # Ugly; yeah
    ani = [a for a in _get_animations() if a.name == name].pop()
    ifaces = [i for i in get_interfaces() if
              i.name in interfaces]

    try:
        assert isinstance(ani, Animation)
        assert isinstance(ifaces, list)
        for iface in ifaces:
            assert isinstance(iface, Interface)
    except AssertionError as e:
        print(ani)
        print(ifaces)
        raise e

    running = _get_running()

    runfile = os.path.join(os.getcwd(), ani.runfile)

    with tempfile.NamedTemporaryFile(
         dir=_runfolder, suffix=".yaml", mode="w") as optionfile:
        yaml.dump({**_merge_parameters(ani.config, options),
                   'sockets': [
                   os.path.join(_runfolder, i.name) for i in ifaces
                   ]}, optionfile)
        optionfile.flush()

        print("Start print config\n\n", file=sys.stderr)
        process = Popen(['cat', optionfile.name])
        print("\n\nEnd print config", file=sys.stderr)

        print("Starting process\n\n", file=sys.stderr)
        process = Popen([runfile, optionfile.name])
        # Sleep for a second to ensure that the cpu is switching to the new
        # processes, ensuring that it loads in the temporary config file which
        # gets deleted after exiting the `with` scope
        time.sleep(1)

    running.append(Running.model_validate({
        'animation': ani,
        'interfaces': ifaces,
        'properties': options,
        'pid': process.pid,
    }))

    _write_running(running)


def stop(name):
    print(f"Stopping animation '{name}'")
    return


def ls():
    for ani in _get_animations():
        print(ani.name)


def running():
    return
