import json
import subprocess

from py_hydropi.lib.modules.inputs import Input


class HomeLabPH(Input):
    provides = ('HOMELAB_PH', 'HOMELABPH')

    def __init__(self, **kwargs):

        e = subprocess.check_output('/var/www/homelab/cgi-bin/get_pH.sh -j; echo 0', shell=True)
        data = [json.loads(r) for r in e.splitlines()][0]
        b = {'taskStatus': 'bad',
             'errorStrings': ['error: No board or no board data'],
             'time': False,
             'v': False,
             't': False,
             'pH': False,
             'calibID': False,
             'calibDate': False}