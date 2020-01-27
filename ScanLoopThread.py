import time

from PyQt5.QtCore import QThread, pyqtSignal
from fake_rpigpio import RPi

import settings


class ScanLoopThread(QThread):
    scanned_signal = pyqtSignal(str)
    clear_label_signal = pyqtSignal()
    set_focus_signal = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.ean = ""

    def __del__(self):
        self.wait()

    def _loop(self):
        time.sleep(1.5)
        self.scanned_ean = ""
        self.scanning = True
        while self.scanning:
            print("SCANNING")
            self.clear_label_signal.emit()
            RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
            while not RPi.GPIO.input(settings.IR_PIN):
                self.set_focus_signal.emit()
                print("!!!")
                RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
                RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.LOW)
                self.scanned_ean = self.ean
                if len(self.scanned_ean) == 13:
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

