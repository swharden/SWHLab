from PyQt4 import QtGui,QtCore
import sys
import numpy as np
import pylab
import time
import glob
import swhlab.core.common as cm
import ui_abfSelect
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
        self.populateFromPath()
        self.btnUse.clicked.connect(self.use)

    def closeEvent(self, event):
        event.accept()
        self.close()

    def close(self):
        QtGui.QApplication.exit()
        sys.exit() #TODO: clean this up!

    def use(self):
        abfs=[]
        for item in self.listWidget.selectedItems():
            abfs.append(item.text().split("\t")[0])
        print("\nABFS:",','.join(abfs))
        self.close()


    def populateFromPath(self,path='SET PATH'):
        if not os.path.exists(path):
            return

        self.btnPath.setText("scanning folder...")
        self.listWidget.clear()
        QtGui.QApplication.processEvents() #this might get slow, so update now
        filesABF,filesSWH,groups=cm.scanABFfolder(path)
        for fname in sorted(filesABF):
            if fname.endswith(".abf"):
                abf=os.path.basename(fname).replace(".abf","")
                parent=cm.getParent2(abf,groups)
                text="%s\t%s"%(abf,cm.determineProtocol(fname))
                bold,fg,bg=False,(0,0,0,255),(255,255,255,255)
                if abf==parent:
                    bold=True
                self.listWidget.addItem(getListItem(text,bold,bg,fg))
                QtGui.QApplication.processEvents()
                #print(dir(self.MainWindow))
        self.btnPath.setText(path)

if __name__=="__main__":
    if not len(sys.argv)==2:
        print("this script needs to be called with a path.")
        sys.argv.append(['./'])
    if not os.path.exists(sys.argv[1]):
        print("path does not exist:",sys.argv[1])
    else:
        print("launching gui at path:",sys.argv[1])
        app = QtGui.QApplication(sys.argv)
        form = ExampleApp()
        form.show()
        form.populateFromPath(sys.argv[1])
        app.exec_()