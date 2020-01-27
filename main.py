import sys
import threading
import time
from functools import partial

import fridgetresources

from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore
from PyQt5.QtCore import QThreadPool, pyqtSignal, QDate
from PyQt5.QtWidgets import QListWidgetItem, QScrollerProperties, QScroller

import settings
from platform_wrapper.models.product import Product
from platform_wrapper.models.products import Products
from platform_wrapper.platform_wrapper import PlatformWrapper
from settings import PAGE_INDEXES
from utils.label_utils import process_keypress_label
from utils.worker import Worker

from widgets.ProductWidget import ProductWidget

try:
    # Since RPi.GPIO doesn't work on windows we need to fake the library if we are developing on other OS
    import RPi.GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpigpio.RPi as RPi


class MainWindow(QtWidgets.QMainWindow):
    scanning = True

    scanned = pyqtSignal(str)
    clear_label_signal = pyqtSignal()

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
        self.clear_label_signal.connect(self._clear_ean_label)

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
        # Custom Products
        self.scan_page.findChild(QtWidgets.QWidget, 'noBarcodeWidget').mouseReleaseEvent = partial(self.switch_page,
                                                                                                   dest="custom_product_page",
                                                                                                   disable_worker=True)

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

        # custom_product_page
        custom_product_page = self.stacked_widget.findChild(QtWidgets.QWidget, 'customProductNamePage')
        self.custom_product_label = self.stacked_widget.findChild(QtWidgets.QLabel, 'productNameLabel')
        self.custom_product_name_label = ""
        next_widget = custom_product_page.findChild(QtWidgets.QWidget, 'nextNameWidget')
        for key in settings.KEYBOARD_KEYS:
            custom_product_page.findChild(QtWidgets.QWidget, key + 'Widget').mouseReleaseEvent = partial(self.update_custom_product_label, label=self.custom_product_label, key=key, next_widget=next_widget)
        custom_product_page.findChild(QtWidgets.QWidget, 'backNameWidget').mouseReleaseEvent = partial(
            self.switch_page,
            dest="scan_page")
        next_widget.mouseReleaseEvent = partial(
            self.switch_page,
            dest="custom_product_expiration_page")

        # custom_product_expiration_page
        custom_product_expiration_page = self.stacked_widget.findChild(QtWidgets.QWidget, 'customProductExpirationPage')
        custom_product_expiration_page.findChild(QtWidgets.QWidget, 'backExpWidget').mouseReleaseEvent = partial(
            self.switch_page,
            dest="custom_product_page")
        self.expiration_calender = custom_product_expiration_page.findChild(QtWidgets.QCalendarWidget,
                                                                            'productExpirationCalenderWidget')
        for d in (QtCore.Qt.Saturday, QtCore.Qt.Sunday):
            fmt = self.expiration_calender.weekdayTextFormat(d)
            fmt.setForeground(QtCore.Qt.black)
            self.expiration_calender.setWeekdayTextFormat(d, fmt)

        custom_product_expiration_page.findChild(QtWidgets.QWidget, 'nextExpWidget').mouseReleaseEvent = partial(
            self.switch_page,
            dest="custom_product_category_page"
        )

        # custom_product_category_page
        custom_product_category_page = self.stacked_widget.findChild(QtWidgets.QWidget, 'customProductCategoryPage')
        for category in settings.CATEGORIES:
            custom_product_category_page.findChild(QtWidgets.QWidget, category + 'CustomCategoryWidget').mouseReleaseEvent = partial(
                self.insert_custom_product,
                category=category)
        custom_product_category_page.findChild(QtWidgets.QWidget, 'backCategoryWidget').mouseReleaseEvent = partial(
            self.switch_page,
            dest="custom_product_expiration_page")

        self._setup_scroll_bars()

        self.show()
        #self.showFullScreen()
        #self.setCursor(QtCore.Qt.BlankCursor)

    def switch_page(self, event=None, dest: str = None, disable_worker: bool = False, load_box: int = None,
                    category: str = None, clearable_list=None):

        """Switch page

        :event event: an event
        :dest string: the destination page, see settings.py
        :disable_worker bool: whether or not the main worker, used for the scanner, should be halted
        :load_box int: which box should be loaded
        :category string: the category, used when filtering
        clearable_list: list which should be cleared
        """

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
            self.scan_page_product_list_view.clear()
            self.products.products.clear()
        elif PAGE_INDEXES[dest] == 12:
            self.soon_expired_products()

        if disable_worker:
            self.event_stop.set()
            self.scanning = False

        self.stacked_widget.setCurrentIndex(PAGE_INDEXES[dest])

    def filter_products(self, category):
        """Filter the inventory by a category and fill the ListWidget

        We use generic page and ListWidget names, based on category.
        Example, the page for Dairy is called dairyPage, the ListWidget is called dairyListWidget, etc.

        :category string: string category
        """

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
        """Filter the inventory by expiration days and fill the ListWidget"""

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
        """Update a product ListWidget

        Used when the amount of a product is changed and the ListWidget and product require updating

        :product Product: the Product object in question
        :category string: the category (used to pick the right page and ListWidget)
        :increase boolean: whether the amount has been increased or not
        :scanner_page boolean: whether we are updating the inventory or simply the list of scanned products
        """

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

    def update_custom_product_label(self, event, label, key, next_widget):
        """Update the display value of the custom product label, used for naming a custom product

        :event event: an event
        :label QtLabel: the label
        :key string: which key has been clicked
        :next_widget: the widget that goes to the next page, disabled when the length is 0 (so that the user
        cannot go to the next page with an empty name)
        """

        self.custom_product_name_label = process_keypress_label(event=event, label=label, value=key)

        if len(self.custom_product_name_label) > 0:
            next_widget.setEnabled(True)
        else:
            next_widget.setEnabled(False)

    def insert_custom_product(self, event, category):
        custom_product = Product(
            product_name=self.custom_product_name_label,
            product_exp=QDate.currentDate().daysTo(self.expiration_calender.selectedDate()),
            product_category=category
        )

        self.products.products.append(custom_product)

        product_item = QListWidgetItem(self.scan_page_product_list_view)
        product_item_widget = ProductWidget(custom_product, self, "scanner", local=True)
        product_item.setSizeHint(product_item_widget.size())
        self.scan_page_product_list_view.addItem(product_item)
        self.scan_page_product_list_view.setItemWidget(product_item, product_item_widget)

        # Clear the used variables
        self.custom_product_name_label = ""
        self.custom_product_label.clear()
        self.expiration_calender.setSelectedDate(QDate.currentDate())

        self.switch_page(event=None, dest="scan_page")

    def add_to_scanned_list_table(self, ean: str):
        """Add a scanned product to the list

        :ean string: the scanned ean
        """
        product = self.platform_api.get_product_from_ean(ean)


        if product is not None:
            self.products.add_product(product)

            product_item = QListWidgetItem(self.scan_page_product_list_view)
            product_item_widget = ProductWidget(product, self, "scanner", local=True)
            product_item.setSizeHint(product_item_widget.size())
            self.scan_page_product_list_view.addItem(product_item)
            self.scan_page_product_list_view.setItemWidget(product_item, product_item_widget)
        self.scan_page_input_label.clear()
        self.scan_page_product_list_view.scrollToBottom()

        time.sleep(1)
        self.scanning = True
        self.worker = Worker(self.scan_loop)
        self.threadpool.start(self.worker)
        self.event_stop.clear()

    def send_products_to_box(self, event=None):
        """Send the scanned products to the box

        """

        # Pause the scanning thread (e.g. prevent the scanner from being able to trigger)
        self.event_stop.set()

        new_products = self.platform_api.add_products(self.products)

        self.scan_page_product_list_view.clear()
        self.products.products.clear()

        self.inventory_products = new_products

    def _clear_ean_label(self):
        self.scan_page_input_label.clear()

    def scan_loop(self):
        """Function which runs our scan loop.

        This functions needs to run in a different thread.
        It starts looking for a signal from our IR sensor, when found it will send a signal
        to the scanner to activate.

        Once it has scanned a barcode it emit a signal to talk with a different thread (the UI thread)
        so that the newly scanned item can be added to the ListWidget.
        """
        time.sleep(1.5)
        while self.scanning:
            self.event_stop.clear()
            RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
            self.clear_label_signal.emit()
            while not self.event_stop.is_set() and not RPi.GPIO.input(settings.IR_PIN):
                self.scan_page_input_label.setFocus()
                RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
                RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.LOW)
                scanned_ean = self.scan_page_input_label.text()
                if len(scanned_ean) == 13:
                    RPi.GPIO.output(settings.SCANNER_PIN, RPi.GPIO.HIGH)
                    self.scanning = False
                    self.event_stop.set()
                    self.scanned.emit(scanned_ean)

    def _setup_scroll_bars(self):
        """Set the properties of all scroll bars

        Scroll bars are selected based on a unique prefix and a common suffix.
        Example: dairy + ListWidget, where the 'ListWidget' suffix is the same for all other list widgets.

        """
        for widget_prefix in settings.ALL_SCROLLABLE_LIST_WIDGETS_PREFIXES:

            list_widget = self.stacked_widget.findChild(QtWidgets.QWidget, widget_prefix + "Page")\
                .findChild(QtWidgets.QListWidget, widget_prefix + "ListWidget")

            sp = QScrollerProperties()
            sp.setScrollMetric(QScrollerProperties.DragVelocitySmoothingFactor, 0.6)
            sp.setScrollMetric(QScrollerProperties.MinimumVelocity, 0.0)
            sp.setScrollMetric(QScrollerProperties.MaximumVelocity, 0.2)
            sp.setScrollMetric(QScrollerProperties.AcceleratingFlickMaximumTime, 0.1)
            sp.setScrollMetric(QScrollerProperties.AcceleratingFlickSpeedupFactor, 1.2)
            sp.setScrollMetric(QScrollerProperties.SnapPositionRatio, 0.2)
            sp.setScrollMetric(QScrollerProperties.MaximumClickThroughVelocity, 1)
            sp.setScrollMetric(QScrollerProperties.DragStartDistance, 0.001)
            sp.setScrollMetric(QScrollerProperties.HorizontalOvershootPolicy, 1)
            sp.setScrollMetric(QScrollerProperties.VerticalOvershootPolicy, 1)

            scroller = QScroller.scroller(list_widget.viewport())
            scroller.setScrollerProperties(sp)
            scroller.grabGesture(list_widget.viewport(), QScroller.LeftMouseButtonGesture)

    def _setup_calendar(self):
        """Set the properties of our expiration calendar
        """
        for d in (QtCore.Qt.Saturday, QtCore.Qt.Sunday):
            fmt = self.expiration_calender.weekdayTextFormat(d)
            fmt.setForeground(QtCore.Qt.black)
            self.expiration_calender.setWeekdayTextFormat(d, fmt)

RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(settings.IR_PIN, RPi.GPIO.IN)
RPi.GPIO.setup(settings.SCANNER_PIN, RPi.GPIO.OUT)
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
