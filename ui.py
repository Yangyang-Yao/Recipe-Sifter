import sys
from PyQt5.QtWidgets import QApplication, QWidget,QLabel,QPushButton,QCheckBox, QComboBox,QLineEdit
from PyQt5.QtGui import QFont
from PyQt5 import QtCore
from solver import Solver

class recipeSift(QWidget):

    def __init__(self):
        self.solver = Solver('index.txt', 'docs.txt', 'pagerank.output')
        super().__init__()
        self.setting()

    def setting(self):
        self.displayNum = 5
        
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        self.setFont(font)
        
        self.query = QLineEdit(self)
        self.query.setFixedWidth(550)
        self.query.setPlaceholderText('Recipe keywords')
        self.query.move(50,25)
        
        self.button = QPushButton('Search', self)
        self.button.clicked.connect(self.search)
        self.button.move(620,25)
        
        font.setPointSize(12)
        self.result = []
        for i in range(self.displayNum):
            self.result.append(QLabel(self))
            self.result[i].setFont(font)
            self.result[i].setGeometry(52, 80 + 70 * i, 700, 70)
            self.result[i].setOpenExternalLinks(True)

        self.setGeometry(500, 100, 800, 800)
        self.setWindowTitle('Recipe Sifter')
        self.show()
        
    def hyperlink(self, url):
        return '<a href="' + url + '">' + url + '</a>'
    
    def parse(self, lst):
        output = ""
        for i in range(len(lst)):
            temp = lst[i] + ""
            newurl = ""
            while len(temp) > 50:
                newurl += temp[:50]
                newurl += "\n"
                temp = temp[50:]
            newurl += temp
            output += ('<a href="' + lst[i] + '">' + newurl + '\n</a>')
        return output
            

    def search(self):
        try:
            lst = self.solver.solve(self.query.text())
            for i in range(min(self.displayNum, len(lst))):
                self.result[i].setText(self.hyperlink(lst[i]))
            self.result[4].setText('<a href="www.google.com">www.google.com</a>')
        except:
            self.result.setText('error')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    Ex = recipeSift()
    exit(app.exec_())
