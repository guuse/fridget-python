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
        productWidget.resize(465, 116)
        productWidget.setStyleSheet("QPushButton{\n"
"    background-color: rgba(99, 169, 159, 1);\n"
"    border-style: solid;\n"
"    border-color:  rgba(99, 169, 159, .5);\n"
"    border-width: 2px;\n"
"    border-radius: 4px;\n"
"    font-weight: 900;\n"
"    font-size: 20px;\n"
"}\n"
"")
        self.gridLayoutWidget = QtWidgets.QWidget(productWidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(360, 0, 97, 111))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.removeButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.removeButton.setMaximumSize(QtCore.QSize(200, 200))
        self.removeButton.setObjectName("removeButton")
        self.gridLayout.addWidget(self.removeButton, 3, 0, 1, 1)
        self.addButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.addButton.setMaximumSize(QtCore.QSize(50, 200))
        self.addButton.setObjectName("addButton")
        self.gridLayout.addWidget(self.addButton, 2, 0, 1, 1)
        self.productAmountLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.productAmountLabel.setMaximumSize(QtCore.QSize(16777215, 15))
        self.productAmountLabel.setStyleSheet("QLabel {\n"
"     qproperty-alignment: \'AlignVCenter | AlignCenter\';\n"
"    font-size: 18px;\n"
"    font-weight: 600;\n"
"}")
        self.productAmountLabel.setObjectName("productAmountLabel")
        self.gridLayout.addWidget(self.productAmountLabel, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_3.setMaximumSize(QtCore.QSize(16777215, 15))
        self.label_3.setStyleSheet("QLabel {\n"
"     qproperty-alignment: \'AlignVCenter | AlignCenter\';\n"
"    font-size: 15px\n"
"}")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.verticalLayoutWidget = QtWidgets.QWidget(productWidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 341, 113))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.productNameLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.productNameLabel.setStyleSheet("QLabel{\n"
"    font-weight: 600;\n"
"    font-size: 18px;\n"
"    margin-left: 10px;\n"
"}")
        self.productNameLabel.setWordWrap(True)
        self.productNameLabel.setObjectName("productNameLabel")
        self.verticalLayout.addWidget(self.productNameLabel)
        self.productDescLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.productDescLabel.setStyleSheet("QLabel{\n"
"    font-size: 14px;\n"
"    margin-left: 10px;\n"
"}")
        self.productDescLabel.setWordWrap(True)
        self.productDescLabel.setObjectName("productDescLabel")
        self.verticalLayout.addWidget(self.productDescLabel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(7)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setStyleSheet("QLabel{\n"
"     qproperty-alignment: \'AlignVCenter | AlignRightr\';\n"
"    font-size: 18px;\n"
"}")
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.productExpInLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.productExpInLabel.setEnabled(True)
        self.productExpInLabel.setMaximumSize(QtCore.QSize(30, 16777215))
        self.productExpInLabel.setStyleSheet("QLabel{\n"
"     qproperty-alignment: \'AlignVCenter | AlignCenter\';\n"
"    font-size: 18px;\n"
"    font-weight: 600\n"
"}")
        self.productExpInLabel.setWordWrap(False)
        self.productExpInLabel.setObjectName("productExpInLabel")
        self.horizontalLayout.addWidget(self.productExpInLabel)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setStyleSheet("QLabel{\n"
"     qproperty-alignment: \'AlignVCenter | AlignLeftr\';\n"
"    font-size: 18px;\n"
"}")
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(productWidget)
        QtCore.QMetaObject.connectSlotsByName(productWidget)

    def retranslateUi(self, productWidget):
        _translate = QtCore.QCoreApplication.translate
        productWidget.setWindowTitle(_translate("productWidget", "Form"))
        self.removeButton.setText(_translate("productWidget", "-"))
        self.addButton.setText(_translate("productWidget", "+"))
        self.productAmountLabel.setText(_translate("productWidget", "-55"))
        self.label_3.setText(_translate("productWidget", "Amount"))
        self.productNameLabel.setText(_translate("productWidget", "productName"))
        self.productDescLabel.setText(_translate("productWidget", "productDesc"))
        self.label.setText(_translate("productWidget", "Expires in:"))
        self.productExpInLabel.setText(_translate("productWidget", "exp"))
        self.label_2.setText(_translate("productWidget", "days"))
