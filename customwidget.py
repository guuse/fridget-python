# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'customwidget.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_productWidget(object):
    def setupUi(self, productWidget):
        productWidget.setObjectName("productWidget")
        productWidget.resize(450, 100)
        productWidget.setStyleSheet("")
        self.productNameLabel = QtWidgets.QLabel(productWidget)
        self.productNameLabel.setGeometry(QtCore.QRect(10, 10, 221, 21))
        self.productNameLabel.setObjectName("productNameLabel")
        self.productDescLabel = QtWidgets.QLabel(productWidget)
        self.productDescLabel.setGeometry(QtCore.QRect(10, 30, 221, 21))
        self.productDescLabel.setObjectName("productDescLabel")
        self.productExpInLabel = QtWidgets.QLabel(productWidget)
        self.productExpInLabel.setGeometry(QtCore.QRect(10, 50, 221, 21))
        self.productExpInLabel.setObjectName("productExpInLabel")
        self.productAmountLabel = QtWidgets.QLabel(productWidget)
        self.productAmountLabel.setGeometry(QtCore.QRect(350, 70, 51, 21))
        self.productAmountLabel.setObjectName("productAmountLabel")
        self.gridLayoutWidget = QtWidgets.QWidget(productWidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(150, 10, 160, 80))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.addButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.addButton.setObjectName("addButton")
        self.gridLayout.addWidget(self.addButton, 0, 0, 1, 1)
        self.removeButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.removeButton.setObjectName("removeButton")
        self.gridLayout.addWidget(self.removeButton, 1, 0, 1, 1)

        self.retranslateUi(productWidget)
        QtCore.QMetaObject.connectSlotsByName(productWidget)

    def retranslateUi(self, productWidget):
        _translate = QtCore.QCoreApplication.translate
        productWidget.setWindowTitle(_translate("productWidget", "Form"))
        self.productNameLabel.setText(_translate("productWidget", "productName"))
        self.productDescLabel.setText(_translate("productWidget", "productDesc"))
        self.productExpInLabel.setText(_translate("productWidget", "productExpsIn"))
        self.productAmountLabel.setText(_translate("productWidget", "productAmnt"))
        self.addButton.setText(_translate("productWidget", "Add"))
        self.removeButton.setText(_translate("productWidget", "Remove"))
