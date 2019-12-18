import sys
import threading
from functools import partial

import fridgetresources_rc

from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import QThreadPool, Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QTableWidgetItem, QListWidgetItem, QWidget

import settings
from customwidget import Ui_productWidget
from datakick_wrapper.datakick_wrapper import DatakickWrapper
from platform_wrapper.models.product import Product
from platform_wrapper.models.products import Products
from platform_wrapper.platform_wrapper import PlatformWrapper
from settings import PAGE_INDEXES
from utils.worker import Worker


class ProductWidget(QWidget, Ui_productWidget):
    def __init__(self, product: Product, *args,**kwargs):
        QWidget.__init__(self,*args,**kwargs)
        self.setupUi(self)
        self.productNameLabel.setText(product.product_name)
        self.productDescLabel.setText(product.product_desc)
        self.productAmountLabel.setText(product.product_amount.__str__())
        self.productExpInLabel.setText(product.product_exp.__str__())
        self.product_id = product.product_id
        self.removeButton.clicked.connect(self._delete_item)

    def _delete_item(self):
        settings.PLATFORM_API.delete_product(self.product_id)

class MainWindow(QtWidgets.QMainWindow):

    products = Products()
    scanning = True

    scanned = pyqtSignal()

    def __init__(self, platform_api: PlatformWrapper, datakick_api, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.threadpool = QThreadPool()
        self.event_stop = threading.Event()

        uic.loadUi("resources/ui/stackedTest.ui", self)

        self.platform_api = platform_api
        self.datakick_api = datakick_api

        self.stacked_widget = self.findChild(QtWidgets.QStackedWidget, 'stackedWidget')
        self.stacked_widget.setCurrentIndex(0)

        self.scanned.connect(self.add_to_table)

        # Unlock Screen
        self.unlock_screen = self.stacked_widget.findChild(QtWidgets.QWidget, 'unlockPage')
        self.unlock_widget = self.unlock_screen.findChild(QtWidgets.QWidget, 'unlockWidget')
        self.unlock_widget.mouseReleaseEvent=partial(self.switch_page, dest="main_page")

        # Main Screen
        self.main_menu_screen = self.stacked_widget.findChild(QtWidgets.QWidget,
                                                              'mainMenuPage')
        self.scan_products_widget = self.main_menu_screen.findChild(QtWidgets.QWidget,
                                                                    'scanWidget')
        self.scan_products_widget.mouseReleaseEvent=partial(self.switch_page,
                                                            dest="scan_page")
        self.inventory_widget = self.main_menu_screen.findChild(QtWidgets.QWidget,
                                                                'inventoryWidget')
        self.inventory_widget.mouseReleaseEvent=partial(self.switch_page,
                                                        dest="inventory_page")

        self.p1 = self.stacked_widget.findChild(QtWidgets.QWidget, 'p1')
        self.scan_page = self.stacked_widget.findChild(QtWidgets.QWidget, 'scanPage')
        self.button = self.p1.findChild(QtWidgets.QPushButton, 'p1ChangePage2Button')
        self.button.clicked.connect(self.switch_to_scan_page)
        self.button2 = self.p1.findChild(QtWidgets.QPushButton, 'changeImgButton')
        self.button2.clicked.connect(self.change_image)
        self.button2 = self.p1.findChild(QtWidgets.QPushButton, 'randomTestButton')
        self.button2.clicked.connect(self.testLoop)
        self.label = self.p1.findChild(QtWidgets.QLabel, 'label1')
        self.table = self.scan_page.findChild(QtWidgets.QTableWidget, 'tableWidget')
        self.button39 = self.scan_page.findChild(QtWidgets.QPushButton, 'pushButton39')
        self.button39.clicked.connect(self.addItem)

        # Scan Page
        self.scan_page_return_main_page_button = self.scan_page.findChild(QtWidgets.QWidget, 'mainMenuWidgetSwitch')
        self.scan_page_return_main_page_button.mouseReleaseEvent=partial(self.switch_page,
                                                                         dest="main_page",
                                                                         disable_worker=True)

        self.scan_page_send_products = self.scan_page.findChild(QtWidgets.QWidget, 'sendProductsWidgetSwitch')
        self.scan_page_send_products.mouseReleaseEvent=self.send_products_to_box

        self.inputLabel = self.scan_page.findChild(QtWidgets.QLineEdit, 'hiddenLineEdit')
        settings.word = self.inputLabel

        # List View Trials
        self.productListView = self.scan_page.findChild(QtWidgets.QListWidget, 'productListWidget')
        self.productListView.itemDoubleClicked.connect(self.deleteItem)

        # Inventory full
        self.inventory_screen = self.stacked_widget.findChild(QtWidgets.QWidget, 'allProductsPage')
        self.fullInventoryListWidget = self.inventory_screen.findChild(QtWidgets.QListWidget, 'allProductsListWidget')
        self.inventory_back_widget = self.inventory_screen.findChild(QtWidgets.QWidget, 'allProductsBackWidget')
        self.inventory_back_widget.mouseReleaseEvent=partial(self.switch_page,
                                                             dest="main_page")

        # TODO: DO THIS ONCE AFTER PICKING BOX, ONLY REFRESH WHEN USER HAS ADDED PRODUCTS?
        self.inventory = self.platform_api.get_products(411)

        #self.showFullScreen()
        self.show()

    def switch_page(self, event=None, dest: str = None, disable_worker: bool = False):

        if PAGE_INDEXES[dest] == 3:
            self.scanning = True
            self.worker = Worker(self.testLoop)
            self.threadpool.start(self.worker)
            self.event_stop.clear()
        elif PAGE_INDEXES[dest] == 1 and disable_worker:
            self.event_stop.set()
            self.scanning = False
            self.productListView.clear()
            self.products.products.clear()
        elif PAGE_INDEXES[dest] == 5:
            self.fullInventoryListWidget.clear()
            print(self.inventory.products_length())
            for product in self.inventory.products:
                product_item = QListWidgetItem(self.fullInventoryListWidget)
                product_item_widget = ProductWidget(product)
                product_item.setSizeHint(product_item_widget.size())
                self.fullInventoryListWidget.addItem(product_item)
                self.fullInventoryListWidget.setItemWidget(product_item, product_item_widget)

        self.stacked_widget.setCurrentIndex(PAGE_INDEXES[dest])

    def unlock_device(self, event):

        self.stacked_widget.setCurrentIndex(1)

    def switch_to_scan_page(self):
        self.stacked_widget.setCurrentIndex(3)
        self.worker = Worker(self.testLoop)
        self.threadpool.start(self.worker)
        self.event_stop.clear()

    def switch_to_first_screen(self):
        self.event_stop.set()
        self.stacked_widget.setCurrentIndex(1)

    def change_image(self):
        pixmap = QtGui.QPixmap("077G.png")
        #self.label.setPixmap(pixmap)

        url = 'http://www.google.com/images/srpr/logo1w.png'
        import urllib.request
        data = urllib.request.urlopen(url).read()

        image = QtGui.QImage()
        image.loadFromData(data)

        self.label.setPixmap(QtGui.QPixmap(image))

    def add_to_list(self, product_ean):
        pass

    def deleteItem(self, item):
        id = self.productListView.currentRow()
        self.productListView.takeItem(id)

    def addItem(self):

        item = QListWidgetItem(self.productListView)
        item_widget = ProductWidget()
        item.setSizeHint(item_widget.size())
        self.productListView.addItem(item)
        self.productListView.setItemWidget(item, item_widget)

    def add_to_table(self):

        product = self.platform_api.get_product_from_ean(self.ean)

        self.products.add_product(product)

        product_item = QListWidgetItem(self.productListView)
        product_item_widget = ProductWidget(product)
        product_item.setSizeHint(product_item_widget.size())
        self.productListView.addItem(product_item)
        self.productListView.setItemWidget(product_item, product_item_widget)

        self.inputLabel.clear()

        self.scanning = True
        self.worker = Worker(self.testLoop)
        self.threadpool.start(self.worker)
        self.event_stop.clear()

    def send_products_to_box(self, event=None):
        self.event_stop.set()

        print(self.inventory.products_length())
        print(self.products.products_length())

        self.platform_api.add_products(self.products)

        self.productListView.clear()
        self.products.products.clear()

    def testLoop(self):
        while self.scanning:
            self.event_stop.clear()
            while not self.event_stop.is_set():

                self.inputLabel.setFocus()

                if len(self.inputLabel.text()) == 13:
                    self.scanning = False
                    self.event_stop.set()

                    self.ean = self.inputLabel.text()

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

            print("!!")

            settings.word.setFocus()

            if len(settings.word.text()) == 2:
                self.event_stop.set()

                self.ean = settings.word

                x = self.scanned.emit()


platform_api = PlatformWrapper(api_key="")
settings.PLATFORM_API = platform_api
datakick_api = DatakickWrapper()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow(settings.PLATFORM_API, datakick_api)
# window.showFullScreen()
sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook

app.exec_()