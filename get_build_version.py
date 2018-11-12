import os
import time

print(os.environ.get('TRAVIS_TAG') or '0.0.0.post{}'.format(int(time.time())))
