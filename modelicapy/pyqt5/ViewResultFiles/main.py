"""
Simple demonstration of creating a GUI using Qt and Python which can make a matplotlib
plot and load a modelica result file.
"""
import sys
from PyQt5 import QtWidgets, QtGui
from generated.MainWindow import Ui_MplMainWindow
from buildingspy.io.outputfile import Reader


class MainWindow(QtWidgets.QMainWindow,Ui_MplMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.mplactionOpen.triggered.connect(self.loadFile)
        self.mplactionQuit.triggered.connect(self.exitApp)
        self.mplpushButton.clicked.connect(self.plotData)

    def exitApp(self):
        self.close()

    def loadFile(self):
        self.fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Modelica Result File", "", "MAT Files (*.mat);;All Files (*)")
        self.labelFileName.setText(self.fileName) 
        self.readData()

    def plotData(self):
        self.readData()
        self.mpl.canvas.ax.clear()
        self.labelError.setText("")
        xyFound = False
        try:
            x, y = self.r.values(self.mpllineEdit.text())
            xyFound = True
        except Exception as e:
            self.labelError.setText(str(e))
        finally:
            pass

        if xyFound:
            self.mpl.canvas.ax.plot(x, y)
            self.mpl.canvas.draw()

    def readData(self):
        self.r = Reader(self.fileName, 'dymola')
        self.varNames = self.r.varNames()


if __name__ == "__main__":
    # Create GUI application
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())