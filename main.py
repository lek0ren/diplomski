from cgenerator import CGenerator 
from parser import Parser
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QTextEdit, QLabel, QComboBox


parser = Parser('textZadatka.txt')
cgenerator = CGenerator('zadaci/sviZadaci.xml')




class GUI:
    app = QApplication([])
    window = QWidget()
    mainLayout = QGridLayout()

    inputCode = QTextEdit()
    answer = QComboBox()
    newCodeWindow = QWidget()
    newCodeLayout = QGridLayout()

    generatedCodeWindow = QWidget()
    generatedCodeLayout = QGridLayout()
    generatedCode = QTextEdit()

    question = 'Pretpostaviti da su sve promenljive tipa int. Koja je slozenost datog algoritma?\n\n\n'


    def __init__(self):
        self.window.setGeometry(200,200,1200,800)
        
        addNewCodeInPascal = QPushButton('Dodaj novu pitalicu u Pascalu')
        addNewCodeInPascal.clicked.connect(self.addNewCodeClicked)
        generateRandomCode = QPushButton('Generisi pitalicu nasumicno')
        generateRandomCode.clicked.connect(self.generateRandomClicked)
        PascalToC = QPushButton('Prevedi Pascal na C')
        PascalToC.clicked.connect(self.PascalToCClicked)
        


        self.mainLayout.addWidget(addNewCodeInPascal,6,0,1,1)
        self.mainLayout.addWidget(generateRandomCode,6,1,1,1)
        self.mainLayout.addWidget(PascalToC,6,2,1,1)
        self.mainLayout.addWidget(self.newCodeWindow,0,0,6,4)
        self.mainLayout.addWidget(self.generatedCodeWindow,0,5,6,4)
        

        self.newCodeLayout.addWidget(QLabel("Pascal kod"), 0,0,1,1)
        self.newCodeLayout.addWidget(self.inputCode,1,0,12,12)
        self.newCodeLayout.addWidget(QLabel("Tacan odgovor"),13,0,1,3)
        self.newCodeLayout.addWidget(self.answer,13,3,1,9)
        self.answer.addItems(["n","n * log(n)","n^2","n^2 * log(n)","n^3","n!","log(n!)","log(n)","sqrt(n)", "n^3/2"])
        self.inputCode.append('probni text')

        self.generatedCodeLayout.addWidget(QLabel("Generisan C kod"))
        self.generatedCodeLayout.addWidget(self.generatedCode,1,0,13,13)
        self.generatedCode.setTabStopWidth(self.generatedCode.fontMetrics().width(' ') * 8)
        

        self.newCodeWindow.setLayout(self.newCodeLayout)
        self.generatedCodeWindow.setLayout(self.generatedCodeLayout)
        self.window.setLayout(self.mainLayout)
        self.window.show()

    def display(self):
        self.app.exec_()


    def addNewCodeClicked(self):
        myfile = open("zadaci/textZadatka.txt", "w")
        text = self.inputCode.toPlainText()
        myfile.write(text + "\nanswer:" + self.answer.currentText()) 
        myfile.close()
        print(self.inputCode.toPlainText())
        parser.resetAllScopes()
        parser.parse()
        print("Writing to file")
        parser.appendToFile()
        self.PascalToCClicked()

    def generateRandomClicked(self):
        cgenerator.setRandomProgram()
        genCode_snippet = cgenerator.generateC()
        self.generatedCode.setText(self.question)
        self.generatedCode.append(genCode_snippet)
        self.generatedCode.append(cgenerator.getAnswers())

    def PascalToCClicked(self):
        parser.resetAllScopes()
        parser.parse()
        cgenerator.setProgram(parser.getCurrentProgram())
        genCode_snippet = cgenerator.generateC()
        self.generatedCode.setText(self.question)
        self.generatedCode.append(genCode_snippet)
        self.generatedCode.append(cgenerator.getAnswers())

gui = GUI()
gui.display()

