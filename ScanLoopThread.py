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

    This runs in a different thread.
    It starts looking for a signal from our IR sensor, when found it will send a signal
    to the scanner to activate.
    Once it has scanned a barcode it emit a signal to talk with a different thread (the UI thread)
    so that the newly scanned item can be added to the ListWidget.

    self.ean is updated every time by the main thread (when the main thread notices that the hidden
    input field has changed).

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

    def _loop(self):
        """Scan loop function

        This function runs a loop, ensures that the barcode scanner is off by sending a singal to the scanner pin.
        The inner loop is active as long as the IR pin is active (e.g. sees something).
        We must set focus on the hidden input field (the scanner literally inserts its scanned value into an active
        field, so we must ensure the hidden field is active).
        We take the self.ean value and put it into a local variable (since it may be updated by the main thread while
        we are still using it, we need to store it locally).
        If the found ean has a length of 13 we stop the loop and return the found ean.
        """
        time.sleep(0.5)
        scanned_ean = ""
        while self.scanning:
            self.clear_label_signal.emit()
            RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
            while not RPi.GPIO.input(settings.IR_PIN) and self.scanning:
                self.set_focus_signal.emit()
                RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
                RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.LOW)
                scanned_ean = self.ean
                if len(self.scanned_ean) == 13:
                    print("EAN FOUND: " + self.scanned_ean)
                    RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
                    self.scanning = False
                    return scanned_ean

    def run(self):
        """Run method of the thread.

        Starts the _loop() and waits for a valid ean to be found, if found it emits a signal to the main thread
        which will add it to the ui.
        """
        ean = self._loop()
        self.scanned_signal.emit(ean)

