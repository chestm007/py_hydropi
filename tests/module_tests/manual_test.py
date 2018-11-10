import time

from py_hydropi.main import RaspberryPiTimer

if __name__ == '__main__':
    pi_timer = RaspberryPiTimer()
    pi_timer._queue_loop = print
    pi_timer.start()
    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        pi_timer.stop()