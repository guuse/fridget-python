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
        self.gridLayoutWidget = QtWidgets.QWidget(productWidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(270, 0, 160, 80))
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
        self.productAmountLabel = QtWidgets.QLabel(productWidget)
        self.productAmountLabel.setGeometry(QtCore.QRect(180, 30, 158, 20))
        self.productAmountLabel.setObjectName("productAmountLabel")
        self.verticalLayoutWidget = QtWidgets.QWidget(productWidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 160, 80))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.productNameLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.productNameLabel.setObjectName("productNameLabel")
        self.verticalLayout.addWidget(self.productNameLabel)
        self.productDescLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.productDescLabel.setObjectName("productDescLabel")
        self.verticalLayout.addWidget(self.productDescLabel)
        self.productExpInLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.productExpInLabel.setObjectName("productExpInLabel")
        self.verticalLayout.addWidget(self.productExpInLabel)

        self.retranslateUi(productWidget)
        QtCore.QMetaObject.connectSlotsByName(productWidget)

    def retranslateUi(self, productWidget):
        _translate = QtCore.QCoreApplication.translate
        productWidget.setWindowTitle(_translate("productWidget", "Form"))
        self.addButton.setText(_translate("productWidget", "Add"))
        self.removeButton.setText(_translate("productWidget", "Remove"))
        self.productAmountLabel.setText(_translate("productWidget", "productAmnt"))
        self.productNameLabel.setText(_translate("productWidget", "productName"))
        self.productDescLabel.setText(_translate("productWidget", "productDesc"))
        self.productExpInLabel.setText(_translate("productWidget", "productExpsIn"))
