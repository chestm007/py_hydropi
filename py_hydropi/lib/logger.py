class Logger(object):
    def warn(self, msg):
        print('WARNING: {}'.format(msg))

    def info(self, msg):
        print('INFO: {}'.format(msg))

    def log(self, msg):
        print(msg)