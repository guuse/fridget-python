from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

import settings
from customwidget import Ui_productWidget
from platform_wrapper.models.product import Product


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