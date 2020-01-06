from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel


class ProductListWidget(QWidget):
    def __init__(self, product_name, parent=None):
        super(QWidget, self).__init__()
        layout = QGridLayout()
        for i in range(4):
            layout.addWidget(QLabel(product_name))