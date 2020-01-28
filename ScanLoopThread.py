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
        self.wait()

    def _loop(self):
        time.sleep(1.5)
        self.scanned_ean = ""
        self.scanning = True
        while self.scanning:
            print("SCANNING")
            self.clear_label_signal.emit()
            RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
            while not RPi.GPIO.input(settings.IR_PIN) and self.scanning:
                self.set_focus_signal.emit()
                print("!!!")
                RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
                RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.LOW)
                self.scanned_ean = self.ean
                print(self.scanned_ean)
                if len(self.scanned_ean) == 13 and self.scanning:
                    print("EAN FOUND")
                    print(self.scanned_ean)
                    RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
                    self.scanning = False

        return self.scanned_ean

    def run(self):
        ean = self._loop()
        print("DEZE EAN")
        print(ean)
        self.scanned_signal.emit(ean)

