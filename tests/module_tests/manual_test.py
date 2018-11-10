from py_hydropi.main import RaspberryPiTimer
import os

if __name__ == '__main__':
    pi_timer = RaspberryPiTimer()
    pi_timer._queue_loop = print
    pi_timer.start()
    pi_timer.stop()