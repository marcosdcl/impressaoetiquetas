from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import fdb
import time
import os

from src.ui import Ui_Main

from src.config.Firebird import Firebird
from src.api.FBprodutos import FBprodutos

from src.utils.Paper import Paper

from src.utils.QTableWidgetHandler import QTableWidgetHandler

from src import DatabaseConfig
from src import About

from src.config.ConfigDB import ConfigDB

class MainWindow(QtWidgets.QMainWindow, Ui_Main.Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        
        #Database setup
        self.startDatabase()

        self.setupQtableWidget()
                        
        self.pbAdd.clicked.connect(self.addOutputRow)
        self.pbRemove.clicked.connect(self.removeOutputRow)
        self.pbGenerate.clicked.connect(self.generate)
        self.pbOpenFolder.clicked.connect(self.openFolder)
        
        self.actionBanco_de_dados.triggered.connect(self.openDatabaseConfig)
        self.actionEtiqueta.triggered.connect(lambda _: self.show_error("Ainda não implementado, aguarde"))
        self.actionFolha.triggered.connect(lambda _: self.show_error("Ainda não implementado, aguarde"))
        self.actionSobre.triggered.connect(self.aboutAction)

        self.showMaximized()
        
    def startDatabase(self):
        table = self.findChild(QtWidgets.QTableWidget, "tableWidget_2")
        self.db = ConfigDB()
        
        if not self.db.get("leDBFile"):
            self.statusbar = QtWidgets.QStatusBar()
            self.statusBar().showMessage('Banco de dados não configurado')
            return
        
        try:
            cur = Firebird(self.db.get("leDBFile"),
                        self.db.get("leLogin"),
                        self.db.get("lePassword")).cur
            fBprodutos = FBprodutos(cur)
        except BaseException as e:
            self.show_error(str(e))
            return
        
        QTableWidgetHandler(self.vlInputTW, table, dataBaseAPI = fBprodutos, addPaging=True, addFilter=True)
        self.statusBar().showMessage('Pronto para uso')
        
    def setupQtableWidget(self):
        self.twOutputItens.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.twOutputItens.setColumnCount(4)
        self.twOutputItens.setHorizontalHeaderLabels(["Codigo", "NomeProduto", "Preço", "Quantidade"])
        
    def addOutputRow(self):
        table = self.findChild(QtWidgets.QTableWidget, "tableWidget_2")
        items = table.selectedItems()
        
        outputNumRows = self.twOutputItens.rowCount()
        self.twOutputItens.setRowCount(outputNumRows + 1)
        
        for index, item in enumerate(items):
            newItem = QtWidgets.QTableWidgetItem(item.text())
            self.twOutputItens.setItem(outputNumRows, index,newItem)
        spinBoxWidget = QtWidgets.QSpinBox()
        spinBoxWidget.setMinimum(1)
        self.twOutputItens.setCellWidget(outputNumRows, 3, spinBoxWidget)
        self.twOutputItens.resizeColumnsToContents()

    def removeOutputRow(self):
        table = self.findChild(QtWidgets.QTableWidget, "twOutputItens")
        items = table.selectedIndexes()
        
        if items:
            table.removeRow(items[0].row())
            
    def generate(self):
        rows = self.twOutputItens.rowCount()

        data = []
        
        for row in range(rows):
            data.append([self.twOutputItens.item(row, 0).text(),
                         self.twOutputItens.item(row, 1).text(),
                         self.twOutputItens.item(row, 2).text(),
                         self.twOutputItens.cellWidget(row, 3).value()])
            
        self.show_error("Ao imprimir, escolha o chrome e imprima na escala \"Ajustar à página\", lembrando de colocar a face a ser impressa virada para frente com a folha de cabeça para baixo")
            
        if len(data) != 0:
            paper = Paper()
            paper.buildPaper(data, self.sbHorizontalPos.value(), self.sbVerticalPos.value())
            

        
    def openDatabaseConfig(self):
        configDialog = DatabaseConfig.MainWindow()
        configDialog.exec()
        self.show_error("Para as alterações entrarem em execução, reinicie a aplicação")
    
    def show_error(self, text):
        msg = QtWidgets.QMessageBox()
        msg.setText(text)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.exec_()
        
    def aboutAction(self):
        aboutDialog = About.MainWindow()
        aboutDialog.exec()
        
    def openFolder(self):
        try:
            os.startfile(os.path.realpath(self.db.get('leOutuput')))
        except BaseException as e:
            self.show_error(str(e))
            
                