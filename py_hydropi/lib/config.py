import yaml
import os


MODULE_CONFIG_FILENAME = 'module_config.yaml'
API_CONFIG_FILENAME = 'api_config.yaml' \
                      ''
if os.environ.get('PY_HYDROPI_TESTING') == 'true':
    default_config_dir = 'py_hydropi/defaults/'
else:
    default_config_dir = '/etc/py_hydropi/'


class BaseConfig(object):
    def __init__(self, config_dir=default_config_dir):
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
        raise NotImplementedError


class ModuleConfig(BaseConfig):
    def __init__(self, config_dir=default_config_dir):
        config_dir += MODULE_CONFIG_FILENAME
        super().__init__(config_dir)

    def _load_config(self):
        with open(self.config_dir + '/' + self.filename, 'r') as config_yaml:
            #self.groups = yaml.load(config_yaml)
            self.config = yaml.load(config_yaml)
            self.lights = self.config.get('lights')  # type: list
            self.water_pumps = self.config.get('water_pumps')  # type: list
            self.air_pumps = self.config.get('air_pumps')  # type: list


class ApiConfig(BaseConfig):
    def __init__(self, config_dir=default_config_dir):
        config_dir += API_CONFIG_FILENAME
        super().__init__(config_dir)

    def _load_config(self):
        with open(self.config_dir + '/' + self.filename, 'r') as config_yaml:
            config = yaml.load(config_yaml)
            self.strict_port_checking = config.get('strict_port_checking')
            self.listen_address = config.get('listen_address')
            self.port = config.get('port')
            self.start = config.get('start')
