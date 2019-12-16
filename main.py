import sys
import threading
from datetime import timedelta

import fridgetresources_rc

import keyboard
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import QThreadPool, Qt
from PyQt5.QtWidgets import QTableWidgetItem, QListWidgetItem

from datakick_wrapper.datakick_wrapper import DatakickWrapper
from platform_wrapper.models.products import Products
from platform_wrapper.platform_wrapper import PlatformWrapper
from utils.worker import Worker


class MainWindow(QtWidgets.QMainWindow):

    products = Products()
    scanning = False

    scanned = ""
    product_ean = ""

    def __init__(self, platform_api: PlatformWrapper, datakick_api, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.threadpool = QThreadPool()
        self.event_stop = threading.Event()

        uic.loadUi("resources/ui/stackedTest.ui", self)

        self.platform_api = platform_api
        self.datakick_api = datakick_api

        self.stacked_widget = self.findChild(QtWidgets.QStackedWidget, 'stackedWidget')
        self.stacked_widget.setCurrentIndex(0)
        self.unlock_screen = self.stacked_widget.findChild(QtWidgets.QWidget, 'unlockPage')
        self.unlock_button = self.unlock_screen.findChild(QtWidgets.QPushButton, 'unlockScreenButton')
        self.unlock_button.clicked.connect(self.unlock_device)

        self.main_menu_screen = self.stacked_widget.findChild(QtWidgets.QWidget, 'mainMenuPage')
        self.scan_products_button = self.main_menu_screen.findChild(QtWidgets.QPushButton, 'scanProductsButton')
        self.scan_products_button.clicked.connect(self.switch_to_scan_page)

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
        self.backButton = self.scan_page.findChild(QtWidgets.QPushButton, 'backButton')
        self.backButton.clicked.connect(self.switch_to_first_screen)
        self.sendProductsButton = self.scan_page.findChild(QtWidgets.QPushButton, 'sendProductsButton')
        self.sendProductsButton.clicked.connect(self.send_products_to_box)
        self.inputLabel = self.scan_page.findChild(QtWidgets.QLineEdit, 'hiddenLineEdit')

        # List View Trials
        self.productListView = self.scan_page.findChild(QtWidgets.QListWidget, 'productListWidget')
        self.productListView.itemDoubleClicked.connect(self.deleteItem)

        #self.showFullScreen()
        self.show()

    def unlock_device(self):
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
        print(item.text())
        id = self.productListView.currentRow()
        self.productListView.takeItem(id)

    def addItem(self):
        products = Products()

        from platform_wrapper.models.product import Product
        products.add_product(Product(product_name="Milk", product_amount=1, product_exp=1, product_category="Zuivel"))
        products.add_product(Product(product_name="Cola", product_amount=2, product_exp=1))
        products.add_product(Product(product_name="Fanta", product_amount=1, product_exp=1))
        products.add_product(Product(product_name="Sprite", product_amount=1, product_exp=1))

        x = products.filter_category("Zuivel")

        for e in x:
            print(e.product_name)

        print("Done")



    def add_to_table(self, product_ean):
        self.event_stop.set()

        print(product_ean)
        from platform_wrapper.models.product import Product

        import datetime

        # 1. Scan code
        # 2. Get code from DB (if available)
        # TODO: HANDLE NOT FOUND?
        #datakick_product = datakick_api.get_product(product_ean)
        #
        # product = Product(product_name=datakick_product.product_name,
        #                   product_desc=datakick_product.desc,
        #                   product_amount=datakick_product.amount,
        #                   product_amount_unit=datakick_product.unit,
        #                   product_exp=(datetime.datetime.now() + timedelta(datakick_product.expiration_time)).date())
        # self.products.add_product(product)

        print(self.inputLabel.text())

        QListWidgetItem(self.inputLabel.text(), self.productListView)

        # rowPosition = self.table.rowCount()
        # self.table.insertRow(rowPosition)
        # self.table.setItem(rowPosition, 0, QTableWidgetItem(self.inputLabel.text()))
        # self.table.scrollToBottom()

        print(self.inputLabel.text())
        print(len(self.inputLabel.text()))
        self.inputLabel.clear()
        self.event_stop.clear()

    def send_products_to_box(self):
        self.event_stop.set()
        self.platform_api.add_products(self.products)

    def testLoop(self):
        while not self.event_stop.is_set():

            self.inputLabel.setFocus()

            scanned = ""
            product_ean = ""

            # while True:
                # if keyboard.is_pressed('enter'):
                #     break
                #
                # scanned += keyboard.read_key()


            # for i in range(0, len(scanned)):
            #     if i % 2 == 0:
            #         if not scanned[i].isalpha():
            #             product_ean += scanned[i]


            if len(self.inputLabel.text()) == 13:
                print("Valid")
                self.add_to_table(product_ean)





platform_api = PlatformWrapper(api_key="")
datakick_api = DatakickWrapper()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow(platform_api, datakick_api)
# window.showFullScreen()
sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook

app.exec_()