from py_hydropi.lib.config import Config
from py_hydropi.main import main as py_hydropi_main


def launch_app():
    py_hydropi_main()


def main():
    config = Config(config_dir='py_hydropi/defaults/config.yaml')
    launch_app()


if __name__ == '__main__':
    main()