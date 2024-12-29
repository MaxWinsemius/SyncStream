import os
import yaml
from pydantic import BaseModel

from config import _runfolder


class Interface(BaseModel):
    name: str

    @property
    def socket(self) -> str:
        return os.path.join(_runfolder, self.name)


class Animation(BaseModel):
    name: str

    @property
    def runfile(self) -> str:
        return "../animations/" + self.name + ".py"

    @property
    def config_file(self) -> str:
        return "../animations/" + self.name + ".yaml"

    @property
    def config(self) -> dict:
        if hasattr(self, '_config'):
            return self._config

        with open(self.config_file) as stream:
            self._config = yaml.safe_load(stream)

        return self._config


class Running(BaseModel):
    # A running animation runs on an interface. It contains the overwritten
    # parameters of a config file.
    animation: Animation
    interfaces: list[Interface]
    properties: dict
    pid: int

    @property
    def config(self) -> dict:
        # Merge properties dict into animation.config dict
        return {**self.animation.config, **self.properties}
