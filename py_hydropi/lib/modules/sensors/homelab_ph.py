import json
import subprocess

from py_hydropi.lib.modules.inputs import Input


class HomeLabPH(Input):
    provides = ('HOMELAB_PH', 'HOMELABPH')

    def __init__(self, value_index=None, **kwargs):
        self.value_index = value_index
        
    def _read(self):
        try:
            e = subprocess.check_output('/var/www/homelab/cgi-bin/get_pH.sh -j; echo 0', shell=True)
            data = [json.loads(r) for r in e.splitlines()][0]
            self.value = data.get(self.value_index)
        except Exception as e:
            self.logger.error(e)

