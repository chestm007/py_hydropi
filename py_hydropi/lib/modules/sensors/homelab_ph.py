import json
import subprocess

from py_hydropi.lib.modules.inputs import Input


class HomeLabPH(Input):
    provides = ('HOMELAB_PH', 'HOMELABPH')
    frequency = 10

    def __init__(self, value_index=None):
        super().__init__()
        self.value_index = value_index

    def _read(self):
        try:
            e = subprocess.check_output('/var/www/homelab/cgi-bin/get_pH.sh -j', shell=True)
            data = json.loads(e.decode('utf-8'))
            self._value = data.get(self.value_index)

        except Exception as e:
            self.logger.error(e)

