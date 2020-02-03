import random
import time

from PyQt5.QtCore import QThread, pyqtSignal

import settings

try:
    # Since RPi.GPIO doesn't work on windows we need to fake the library if we are developing on other OS
    import RPi.GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpigpio.RPi as RPi


class ScanLoopThread(QThread):
    """Class which runs our scan loop.

    This needs to run in a different thread.
    It starts looking for a signal from our IR sensor, when found it will send a signal
    to the scanner to activate.
    Once it has scanned a barcode it emit a signal to talk with a different thread (the UI thread)
    so that the newly scanned item can be added to the ListWidget.
    """
    set_focus_signal = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.ean = ""
        self.ean_scanned = False
        self.scanning = True
        self.keep_thread_alive = True

    def __del__(self):
        self.wait()

    def stop(self):
        self.scanning = False
        self.keep_thread_alive = False
        self.wait(1)

    def _loop(self):
        """Scan loop function

        This function runs a loop, ensures that the barcode scanner is off by sending a singal to the scanner pin.
        The inner loop is active as long as the IR pin is active (e.g. sees something).
        We must set focus on the hidden input field (the scanner literally inserts its scanned value into an active
        field, so we must ensure the hidden field is active).

        The scanning variable (self.scanning) is set to false when a ean has read, this is done by the main thread.
        """
        while self.keep_thread_alive:
            while self.scanning:
                RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
                while not RPi.GPIO.input(settings.IR_PIN) and self.scanning:
                    self.set_focus_signal.emit()
                    RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
                    RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.LOW)
                    time.sleep(1.5)

    def run(self):
        self.keep_thread_alive = True
        self.scanning = True
        self._loop()
