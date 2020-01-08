import sys
import threading
import time
from functools import partial

import fridgetresources_rc

from PyQt5 import QtWidgets, uic, QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QThreadPool, Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QTableWidgetItem, QListWidgetItem, QWidget

import settings
from customwidget import Ui_productWidget
from platform_wrapper.models.product import Product
from platform_wrapper.models.products import Products
from platform_wrapper.platform_wrapper import PlatformWrapper
from settings import PAGE_INDEXES
from utils.worker import Worker

import importlib.util
try:
    # Since RPi.GPIO doesn't work on windows we need to fake the library if we are developing on other OS
    importlib.util.find_spec('RPi.GPIO')
    import RPi.GPIO as GPIO
except ImportError:
    import FakeRPi.GPIO as GPIO


class ProductWidget(QWidget, Ui_productWidget):
    delete_signal = pyqtSignal(Product, str, bool, bool)
    increase_signal = pyqtSignal(Product, str, bool, bool)

    def __init__(self, product: Product, mainWindow, category: str, scanner: bool = False, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.productNameLabel.setText(product.product_name)
        self.productDescLabel.setText(product.product_desc)
        self.productAmountLabel.setText(product.product_amount.__str__())
        self.productExpInLabel.setText(product.product_exp.__str__())
        self.product = product
        self.removeButton.clicked.connect(self._delete_item)
        self.addButton.clicked.connect(self._add_item)
        self.main_window = mainWindow
        self.delete_signal.connect(mainWindow.update_products_widget)
        self.increase_signal.connect(mainWindow.update_products_widget)
        self.category = category
        self.is_scanner_page = scanner

    def _add_item(self):
        succeeded = True

        if not self.is_scanner_page:
            succeeded = settings.PLATFORM_API.set_amount_product(self.product.product_id,
                                                 self.product.product_amount + 1)
        if succeeded:
            self.increase_signal.emit(self.product, self.category, True, self.is_scanner_page)

    def _delete_item(self):
        succeeded = True

        if self.product.product_amount == 1 and not self.is_scanner_page:
            succeeded = settings.PLATFORM_API.delete_product(self.product.product_id)
        elif not self.is_scanner_page:
            succeeded = settings.PLATFORM_API.set_amount_product(self.product.product_id,
                                                                 self.product.product_amount - 1)

        if succeeded:
            self.delete_signal.emit(self.product, self.category, False, self.is_scanner_page)


class MainWindow(QtWidgets.QMainWindow):
    scanning = True

    scanned = pyqtSignal()

    def __init__(self, platform_api: PlatformWrapper, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.threadpool = QThreadPool()
        self.event_stop = threading.Event()

        uic.loadUi("resources/ui/main/fridgettwo.ui", self)

        self.platform_api = platform_api

        # Grab the main stacked widget, this stacked widget contains our different pages.
        self.stacked_widget = self.findChild(QtWidgets.QStackedWidget, 'mainStackedWidget')
        self.stacked_widget.setCurrentIndex(0)

        # Create a signal so that we can interact between 2 widgets
        self.scanned.connect(self.add_to_scanned_list_table)

        # unlock_page
        self.unlock_page = self.stacked_widget.findChild(QtWidgets.QWidget, 'unlockPage')
        self.unlock_widget = self.unlock_page.findChild(QtWidgets.QWidget, 'unlockWidget')
        # Switch to the users_page when the unlockWidget is clicked
        self.unlock_widget.mouseReleaseEvent = partial(self.switch_page, dest="users_page")

        # users_page
        self.users_page = self.stacked_widget.findChild(QtWidgets.QWidget, 'usersPage')
        self.user1widget = self.users_page.findChild(QtWidgets.QWidget, 'userOneWidget')
        # Switch to the main_page when the user1widget is clicked
        self.user1widget.mouseReleaseEvent = partial(self.switch_page, dest="main_page", load_box=411)

        # main_page
        self.main_menu_page = self.stacked_widget.findChild(QtWidgets.QWidget, 'mainMenuPage')
        self.main_menu_switch_scan = self.main_menu_page.findChild(QtWidgets.QWidget, 'scanWidget')
        # Switch to the scan_page when the scanWidget is clicked
        self.main_menu_switch_scan.mouseReleaseEvent = partial(self.switch_page, dest="scan_page")
        self.main_menu_switch_inv = self.main_menu_page.findChild(QtWidgets.QWidget, 'inventoryWidget')
        # Switch to the inventory_page when the inventoryWidget is clicked
        self.main_menu_switch_inv.mouseReleaseEvent = partial(self.switch_page, dest="inventory_page")
        self.main_menu_switch_exp = self.main_menu_page.findChild(QtWidgets.QWidget, 'expirationWidget')
        # Switch to the expirations_page when the experationWidget is clicked
        self.main_menu_switch_exp.mouseReleaseEvent = partial(self.switch_page, dest="expirations_page")
        self.main_menu_switch_users = self.main_menu_page.findChild(QtWidgets.QWidget, 'mainMenuToUsersWidget')
        # Switch to the users_page when the mainMenuToUsersWidget is clicked
        self.main_menu_switch_users.mouseReleaseEvent = partial(self.switch_page, dest="users_page")

        # scan_page
        self.scan_page = self.stacked_widget.findChild(QtWidgets.QWidget, 'scannerPage')
        self.scan_page_switch_main_menu = self.scan_page.findChild(QtWidgets.QWidget, 'scanToMainMenuWidget')
        # Switch to the main_page when the scanToMainMenuWidget is clicked (also, disable the scanner, which runs on
        # a worker)
        self.scan_page_switch_main_menu.mouseReleaseEvent = partial(self.switch_page, dest="main_page",
                                                                    disable_worker=True)
        self.scan_page_send_to_fridge = self.scan_page.findChild(QtWidgets.QWidget, 'sendToFridgeWidget')
        # Send products to the fridge when the sendToFridgeWidget is clicked
        self.scan_page_send_to_fridge.mouseReleaseEvent = self.send_products_to_box
        # Grab the hidden LineEdit, used to score the scanned EAN
        self.scan_page_input_label = self.scan_page.findChild(QtWidgets.QLineEdit, 'hiddenEanLineEdit')
        # ListView for scanned items
        self.scan_page_product_list_view = self.scan_page.findChild(QtWidgets.QListWidget, 'scannerListWidget')
        # ??? self.scan_page_product_list_view.itemDoubleClicked.connect(self.deleteItem)

        # inventory_page
        self.inventory_page = self.stacked_widget.findChild(QtWidgets.QWidget, 'inventoryPage')
        self.inventory_page_switch_main_menu = self.inventory_page.findChild(QtWidgets.QWidget,
                                                                             'inventoryToMainMenuWidget')
        # Switch to the main_page when the inventoryToMainMenuWidget is clicked
        self.inventory_page_switch_main_menu.mouseReleaseEvent = partial(self.switch_page, dest="main_page")
        self.inventory_page.findChild(QtWidgets.QWidget, 'fruitsWidget').mouseReleaseEvent = partial(self.switch_page,
                                                                                                     dest="fruit_page",
                                                                                                     category="fruit")
        self.inventory_page.findChild(QtWidgets.QWidget, 'vegetablesWidget').mouseReleaseEvent = partial(
            self.switch_page, dest="vegetable_page", category="vegetable")
        self.inventory_page.findChild(QtWidgets.QWidget, 'dairiesWidget').mouseReleaseEvent = partial(self.switch_page,
                                                                                                      dest="dairy_page",
                                                                                                      category="dairy")
        self.inventory_page.findChild(QtWidgets.QWidget, 'meatsWidget').mouseReleaseEvent = partial(self.switch_page,
                                                                                                    dest="meat_page",
                                                                                                    category="meat")
        self.inventory_page.findChild(QtWidgets.QWidget, 'spreadsWidget').mouseReleaseEvent = partial(self.switch_page,
                                                                                                      dest="spread_page",
                                                                                                      category="spread")
        self.inventory_page.findChild(QtWidgets.QWidget, 'saucesWidget').mouseReleaseEvent = partial(self.switch_page,
                                                                                                     dest="sauce_page",
                                                                                                     category="sauce")
        self.inventory_page.findChild(QtWidgets.QWidget, 'drinksWidget').mouseReleaseEvent = partial(self.switch_page,
                                                                                                     dest="drink_page",
                                                                                                     category="drink")
        self.inventory_page.findChild(QtWidgets.QWidget, 'othersWidget').mouseReleaseEvent = partial(self.switch_page,
                                                                                                     dest="other_page",
                                                                                                     category="other")

        # expiration_page
        self.expirations_page = self.stacked_widget.findChild(QtWidgets.QWidget, 'expirationsPage')
        self.expirations_page_switch_main_menu = self.expirations_page.findChild(QtWidgets.QWidget,
                                                                                 'expirationsToMainMenuPage')
        self.exp_list_widget = self.expirations_page.findChild(QtWidgets.QListWidget, 'expirationsListWidget')

        self.products = Products()
        self.inventory_products = Products()

        # self.showFullScreen()
        self.show()

    def switch_page(self, event=None, dest: str = None, disable_worker: bool = False, load_box: int = None,
                    category: str = None, clearable_list=None):

        if category:
            self.filter_products(category)
        if load_box:
            self.inventory_products = self.platform_api.get_products(load_box)
        if clearable_list:
            clearable_list.clear()
        if PAGE_INDEXES[dest] == 13:
            self.scanning = True
            self.worker = Worker(self.scan_loop)
            self.threadpool.start(self.worker)
            self.event_stop.clear()
        elif PAGE_INDEXES[dest] == 2 and disable_worker:
            self.event_stop.set()
            self.scanning = False
            self.scan_page_product_list_view.clear()
            self.products.products.clear()
        elif PAGE_INDEXES[dest] == 12:
            self.soon_expired_products()

        self.stacked_widget.setCurrentIndex(PAGE_INDEXES[dest])

    def setup_widget_switch_on_click(self, parent, widget_name, destination):
        parent.findChild(QtWidgets.QWidget, widget_name).mouseReleaseEvent = partial(self.switch_page,
                                                                                     dest=destination)

    def filter_products(self, category):

        filtered_products = self.inventory_products.filter_category(category)

        page = self.stacked_widget.findChild(QtWidgets.QWidget, category + "Page")
        list = page.findChild(QtWidgets.QListWidget, category + "ListWidget")
        for product in filtered_products:
            product_item = QListWidgetItem(list)
            product_item_widget = ProductWidget(product, self, category)
            product_item.setSizeHint(product_item_widget.size())
            list.addItem(product_item)
            list.setItemWidget(product_item, product_item_widget)
        page.findChild(QtWidgets.QWidget, category + "BackWidget").mouseReleaseEvent = partial(self.switch_page,
                                                                                               dest="inventory_page",
                                                                                               clearable_list=list)

    def soon_expired_products(self):

        soon_expired_products = self.inventory_products.filter_exp(3)

        for product in soon_expired_products:
            product_item = QListWidgetItem(self.exp_list_widget)
            product_item_widget = ProductWidget(product, self, "expirations")
            product_item.setSizeHint(product_item_widget.size())
            self.exp_list_widget.addItem(product_item)
            self.exp_list_widget.setItemWidget(product_item, product_item_widget)

        self.expirations_page.findChild(QtWidgets.QWidget, "expirationBackWidget").mouseReleaseEvent = partial(self.switch_page,
                                                                                               dest="main_page",
                                                                                               clearable_list=self.exp_list_widget)

    def update_products_widget(self, product: Product, category: str, increase: bool = True, scanner_page: bool = True):
        page = self.stacked_widget.findChild(QtWidgets.QWidget, category + "Page")
        list = page.findChild(QtWidgets.QListWidget, category + "ListWidget")

        all_items = list.findItems('', QtCore.Qt.MatchRegExp)
        row = 0
        widget = None
        for item in all_items:
            widget = list.itemWidget(item)
            if list.itemWidget(item).product == product:
                break
            row += 1

        if increase:
            if widget:
                widget.product.product_amount += 1
                widget.productAmountLabel.setText(widget.product.product_amount.__str__())
        else:
            if widget and widget.product.product_amount == 1:
                list.takeItem(row)
                if scanner_page:
                    self.products.products.remove(widget.product)
                else:
                    self.inventory_products.products.remove(widget.product)
            else:
                widget.product.product_amount -= 1
                widget.productAmountLabel.setText(widget.product.product_amount.__str__())

    def unlock_device(self, event):

        self.stacked_widget.setCurrentIndex(1)

    def switch_to_scan_page(self):
        self.stacked_widget.setCurrentIndex(3)
        self.worker = Worker(self.scan_loop)
        self.threadpool.start(self.worker)
        self.event_stop.clear()

    def switch_to_first_screen(self):
        self.event_stop.set()
        self.stacked_widget.setCurrentIndex(1)

    def change_image(self):
        pixmap = QtGui.QPixmap("077G.png")
        # self.label.setPixmap(pixmap)

        url = 'http://www.google.com/images/srpr/logo1w.png'
        import urllib.request
        data = urllib.request.urlopen(url).read()

        image = QtGui.QImage()
        image.loadFromData(data)

        self.label.setPixmap(QtGui.QPixmap(image))

    def add_to_list(self, product_ean):
        pass

    def deleteItem(self, item):
        id = self.scan_page_product_list_view.currentRow()
        self.scan_page_product_list_view.takeItem(id)

    def addItem(self):

        item = QListWidgetItem(self.scan_page_product_list_view)
        item_widget = ProductWidget()
        item.setSizeHint(item_widget.size())
        self.scan_page_product_list_view.addItem(item)
        self.scan_page_product_list_view.setItemWidget(item, item_widget)

    def add_to_scanned_list_table(self):

        product = self.platform_api.get_product_from_ean(self.ean)

        self.products.add_product(product)

        product_item = QListWidgetItem(self.scan_page_product_list_view)
        product_item_widget = ProductWidget(product, self, "scanner", True)
        product_item.setSizeHint(product_item_widget.size())
        self.scan_page_product_list_view.addItem(product_item)
        self.scan_page_product_list_view.setItemWidget(product_item, product_item_widget)

        self.scan_page_input_label.clear()

        time.sleep(1)
        self.scanning = True
        self.worker = Worker(self.scan_loop)
        self.threadpool.start(self.worker)
        self.event_stop.clear()

    def send_products_to_box(self, event=None):
        self.event_stop.set()

        new_products = self.platform_api.add_products(self.products)

        self.scan_page_product_list_view.clear()
        self.products.products.clear()

        self.inventory_products = new_products

    def scan_loop(self):
        time.sleep(1.5)
        while self.scanning:
            self.event_stop.clear()
            GPIO.output(settings.SCANNER_PIN, GPIO.HIGH)
            while not self.event_stop.is_set() and not GPIO.input(settings.IR_PIN):

                self.scan_page_input_label.setFocus()
                GPIO.output(settings.SCANNER_PIN, GPIO.HIGH)
                GPIO.output(settings.SCANNER_PIN, GPIO.LOW)

                if len(self.scan_page_input_label.text()) == 13:
                    GPIO.output(settings.SCANNER_PIN, GPIO.HIGH)
                    self.scanning = False
                    self.event_stop.set()

                    self.ean = self.scan_page_input_label.text()

                    self.scanned.emit()


class Scanner(QObject):

    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.event_stop = threading.Event()
        self.worker = Worker(self.scan_loop())
        self.threadpool.start(self.worker)
        self.event_stop.set()

    def start_worker(self):
        self.event_stop.clear()

    def stop_worker(self):
        self.event_stop.set()

    def scan_loop(self):
        while not self.event_stop.is_set():

            settings.word.setFocus()

            if len(settings.word.text()) == 2:
                self.event_stop.set()

                self.ean = settings.word

                x = self.scanned.emit()

GPIO.setmode(GPIO.BCM)
GPIO.setup(settings.IR_PIN, GPIO.IN)
GPIO.setup(settings.SCANNER_PIN, GPIO.OUT)
platform_api = PlatformWrapper(api_key="")
settings.PLATFORM_API = platform_api

app = QtWidgets.QApplication(sys.argv)
window = MainWindow(settings.PLATFORM_API)
# window.showFullScreen()
sys._excepthook = sys.excepthook


def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


sys.excepthook = exception_hook

app.exec_()
