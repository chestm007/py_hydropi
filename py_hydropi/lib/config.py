import yaml
import os
from .python_extras import AttrDict

if os.environ['PY_HYDROPI_TESTING'] == 'true':
    print(os.path.curdir)
    config_dir = 'py_hydropi/defaults/config.yaml'
else:
    config_dir = '/etc/py_hydropi/config.yaml'


class Config(object):
    def __init__(self, config_dir=config_dir):
        assert '.yaml' in config_dir

        path = '/'.join(a for a in config_dir.split('/') if not a.endswith('.yaml'))
        self.filename = '/'.join(a for a in config_dir.split('/') if a.endswith('.yaml'))
        self.config_dir = path

        if os.path.isdir(self.config_dir):
            self._load_config()
        else:
            os.mkdir(self.config_dir)
            # TODO: generate default config file

    def _load_config(self):
        with open(self.config_dir + '/' + self.filename, 'r') as config_yaml:
            config = yaml.load(config_yaml)
            config = AttrDict(config)
            self.lights = config.lights  # type: list
            self.water_pumps = config.water_pumps  # type: list
            self.air_pumps = config.air_pumps  # type: list
