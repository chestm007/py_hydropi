import time

import requests

from module_tests.base_test_object import BaseTestObject
from py_hydropi.main import RaspberryPiTimer


class TestApi(BaseTestObject):
    pi_timer = None

    @staticmethod
    def get_url(endpoint=''):
        return 'http://127.0.0.1:8084/api/{}'.format(endpoint)

    @classmethod
    def setUpClass(cls):
        cls.pi_timer = RaspberryPiTimer()
        cls.pi_timer._queue_loop = print
        cls.pi_timer.start()
        start_time = time.time()
        while not requests.get(cls.get_url(), timeout=1.0):
            if time.time() - start_time > 10:
                cls.skipTest('timeout starting API')
        # at this point we can safely assume the API is up and running

    def test_controller_endpoint(self):
        controller_response = requests.get(self.get_url('controllers'))
        self.assertEqual(controller_response.status_code, 200)
        self.assertIsNotNone(controller_response.json())

    def test_output_endpoint(self):
        output_response = requests.get(self.get_url('outputs'))
        self.assertEqual(output_response.status_code, 200)
        self.assertIsNotNone(output_response.json())

    def test_api_endpoint(self):
        api_response = requests.get(self.get_url())
        self.assertEqual(api_response.status_code, 200)
        api_response_json = api_response.json()
        for endpoint in ('controllers', 'outputs'):
            self.assertIn(endpoint, api_response_json)

    @classmethod
    def tearDownClass(cls):
        cls.pi_timer.stop()
