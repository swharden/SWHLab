# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_abfSelect.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(403, 544)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.btnPath = QtGui.QPushButton(self.centralwidget)
        self.btnPath.setObjectName(_fromUtf8("btnPath"))
        self.verticalLayout.addWidget(self.btnPath)
        self.listWidget = QtGui.QListWidget(self.centralwidget)
        self.listWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.listWidget.setAlternatingRowColors(False)
        self.listWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.listWidget.setSelectionRectVisible(True)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        item = QtGui.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtGui.QListWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.listWidget.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtGui.QListWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(211, 250, 200, 200))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.NoBrush)
        item.setForeground(brush)
        self.listWidget.addItem(item)
        self.verticalLayout.addWidget(self.listWidget)
        self.btnUse = QtGui.QPushButton(self.centralwidget)
        self.btnUse.setObjectName(_fromUtf8("btnUse"))
        self.verticalLayout.addWidget(self.btnUse)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "ABF selector", None))
        self.btnPath.setText(_translate("MainWindow", "X:Data2P0120162016-07-11 PIR TR IHC", None))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("MainWindow", "test", None))
        item = self.listWidget.item(1)
        item.setText(_translate("MainWindow", "test2", None))
        item = self.listWidget.item(2)
        item.setText(_translate("MainWindow", "test6", None))
        item = self.listWidget.item(3)
        item.setText(_translate("MainWindow", "test3", None))
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.btnUse.setText(_translate("MainWindow", "Use selected ABFs", None))

