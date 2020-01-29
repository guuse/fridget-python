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
    scanned_signal = pyqtSignal(str)
    clear_label_signal = pyqtSignal()
    set_focus_signal = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.ean = ""
        self.scanning = True

    def __del__(self):
        self.wait()

    def stop(self):
        self.scanning = False
        print("SET TO FALSE")
        self.wait(1)

    def _loop(self):
        time.sleep(2)
        self.scanned_ean = ""
        self.scanning = True
        while self.scanning:
            RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
            while not RPi.GPIO.input(settings.IR_PIN) and self.scanning:
                print("IR ACTIVE")
                self.set_focus_signal.emit()
                self.clear_label_signal.emit()
                time.sleep(0.2)
                print("ACTIVATING SCANNER"+random.randint(0,40).__str__())
                RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
                RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.LOW)
                time.sleep(0.2)
                self.scanned_ean = self.ean
                if len(self.scanned_ean) == 13:
                    print("EAN FOUND")
                    print(self.scanned_ean)
                    RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
                    self.scanning = False

                    return self.scanned_ean

        return None

    def run(self):
        print("Starting thread again")
        ean = self._loop()
        print("DEZE EAN")
        print(ean)
        if ean:
            self.scanned_signal.emit(ean)

