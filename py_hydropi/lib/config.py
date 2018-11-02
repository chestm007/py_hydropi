import yaml
import os


MODULE_CONFIG_FILENAME = 'module_config.yaml'
API_CONFIG_FILENAME = 'api_config.yaml'
METRICS_CONFIG_FILENAME = 'metrics.yaml'

if os.environ.get('PY_HYDROPI_TESTING', '').lower() == 'true':
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
        with open(self.config_dir + '/' + self.filename, 'r') as config_yaml:
            self.config = yaml.load(config_yaml)
            self._config_parser()

    def _config_parser(self):
        pass


class ModuleConfig(BaseConfig):
    def __init__(self, config_dir=default_config_dir):
        config_dir += MODULE_CONFIG_FILENAME
        super().__init__(config_dir)


class MetricsConfig(BaseConfig):
    def __init__(self, config_dir=default_config_dir):
        config_dir += METRICS_CONFIG_FILENAME
        self.enabled = False
        super().__init__(config_dir)

    def _config_parser(self):
        if self.config.get('reporter'):
            self.enabled = True
            self.reporter = list(self.config.get('reporter').keys())[0]


class ApiConfig(BaseConfig):
    def __init__(self, config_dir=default_config_dir):
        config_dir += API_CONFIG_FILENAME
        super().__init__(config_dir)

    def _config_parser(self):
        self.strict_port_checking = self.config.get('strict_port_checking')
        self.listen_address = self.config.get('listen_address')
        self.port = self.config.get('port')
        self.start = self.config.get('start')
