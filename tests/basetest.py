from py_hydropi.lib.config import Config

def main():
    config = Config(config_dir='py_hydropi/defaults/config.yaml')
    print(config)
    print(config.lights)
    print('yay')
if __name__ == '__main__':
    main()