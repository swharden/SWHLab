from PyQt4 import QtGui,QtCore
import sys
import numpy as np
import pylab
import time
import glob
import swhlab.core.common as cm
#import ui_abfSelect
from swhlab.origin import ui_abfSelect
import os
import swhlab

def getListItem(text="stuff",bold=False,bg=(255,255,255,255),fg=(0,0,0,255)):
    item = QtGui.QListWidgetItem(text)
    font = QtGui.QFont()
    if bold:
        font.setBold(True)
        font.setWeight(75)
    item.setFont(font)
    brush = QtGui.QBrush(QtGui.QColor(*bg))
    brush.setStyle(QtCore.Qt.SolidPattern)
    item.setBackground(brush)
    brush = QtGui.QBrush(QtGui.QColor(*fg))
    brush.setStyle(QtCore.Qt.SolidPattern)
    item.setForeground(brush)
    return item

class ExampleApp(QtGui.QMainWindow, ui_abfSelect.Ui_MainWindow):
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)
        self.btnUse.clicked.connect(self.use)
        self.ABFS=[] # we will eventually return this
        self.path="SETTHIS"

    def closeEvent(self, event):
        self.close()

    def use(self):
        for item in self.listWidget.selectedItems():
            self.ABFS.append(item.text().split("\t")[0])
        self.closeEvent(None)

    def populateFromPath(self):
        if not os.path.exists(self.path):
            return
        else:
            self.btnPath.setText("scanning folder...")
            self.listWidget.clear()
            QtGui.QApplication.processEvents() #this might get slow, so update now
            filesABF,filesSWH,groups=cm.scanABFfolder(self.path)
            for fname in sorted(filesABF):
                if fname.endswith(".abf"):
                    abf=os.path.basename(fname).replace(".abf","")
                    parent=cm.getParent2(abf,groups)
                    text="%s\t%s"%(abf,cm.determineProtocol(fname))
                    bold,fg,bg=False,(0,0,0,255),(255,255,255,255)
                    if abf==parent:
                        bold=True
                    if not self.isVisible():
                        print("CLOSING EARLY")
                        #self.closeEvent(None)
                        return # we have already closed
                    self.listWidget.addItem(getListItem(text,bold,bg,fg))
                    QtGui.QApplication.processEvents()
            self.btnPath.setText(self.path)


def getABFlist(path):
    app = QtGui.QApplication(sys.argv)
    form = ExampleApp()
    form.show()
    form.path=path
    QtCore.QTimer.singleShot(0, form.populateFromPath) # shoot this off from inside the main loop
    app.exec() # do the main program loop
    #print("ABFS:",form.ABFS)
    return form.ABFS

if __name__=="__main__":
    print("DONT RUN THIS DIRECTLY!")
    getABFlist(r"X:\Data\2P01\2016\2016-07-11 PIR TR IHC")