from cgenerator import CGenerator 
from parser import Parser
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QTextEdit, QLabel, QComboBox
from docxtpl import DocxTemplate, Listing

parser = Parser('textZadatka.txt')
cgenerator = CGenerator('zadaci/sviZadaci.xml')




class GUI:
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("Softverski sistem za generisanje test pitanja iz analize složenosti na programskom jeziku C")
    mainLayout = QGridLayout()

    inputCode = QTextEdit()
    answer = QComboBox()
    newCodeWindow = QWidget()
    newCodeLayout = QGridLayout()

    generatedCodeWindow = QWidget()
    generatedCodeLayout = QGridLayout()
    generatedCode = QTextEdit()

    genCode_snippet = ''

    question = 'Pretpostaviti da su sve promenljive tipa int. Koja je slozenost datog algoritma?\n\n\n'


    def __init__(self):
        self.window.setGeometry(200,200,1200,800)
        
        addNewCodeInPascal = QPushButton('Sacuvaj uneti Pascal kod u bazu')
        addNewCodeInPascal.clicked.connect(self.addNewCodeClicked)
        generateRandomCode = QPushButton('Generisi pitalicu nasumicno iz baze')
        generateRandomCode.clicked.connect(self.generateRandomClicked)
        PascalToC = QPushButton('Generisi pitalicu na osnovu Pascal koda')
        PascalToC.clicked.connect(self.PascalToCClicked)
        GenerateWord = QPushButton('Sacuvaj pitalicu kao Word dokument')
        GenerateWord.clicked.connect(self.GenerateWordClicked)
        


        self.mainLayout.addWidget(addNewCodeInPascal,6,0,1,1)
        self.mainLayout.addWidget(generateRandomCode,6,7,1,1)
        self.mainLayout.addWidget(GenerateWord,6,8,1,1)
        self.mainLayout.addWidget(PascalToC,6,1,1,1)
        self.mainLayout.addWidget(self.newCodeWindow,0,0,6,4)
        self.mainLayout.addWidget(self.generatedCodeWindow,0,5,6,4)
        

        self.newCodeLayout.addWidget(QLabel("Unesite kod u programskom jeziku Pascal"), 0,0,1,1)
        self.newCodeLayout.addWidget(self.inputCode,1,0,24,24)
        self.newCodeLayout.addWidget(QLabel("Unesite slozenost koda"),25,0,1,6)
        self.newCodeLayout.addWidget(self.answer,25,6,1,18)
        self.answer.addItems(["n","n * log(n)","n^2","n^2 * log(n)","n^3","n!","log(n!)","log(n)","sqrt(n)", "n^3/2"])

        self.generatedCodeLayout.addWidget(QLabel("Generisana pitalica u programskom jeziku C"),0,0,1,1)
        self.generatedCodeLayout.addWidget(self.generatedCode,1,0,24,24)
        self.generatedCodeLayout.addWidget(QLabel(""),25,0,1,1)
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
        self.genCode_snippet = cgenerator.generateC()
        self.generatedCode.setText(self.question)
        self.generatedCode.append(self.genCode_snippet)
        self.generatedCode.append(cgenerator.getAnswers())

    def GenerateWordClicked(self):
        doc = DocxTemplate("templates/one_program2.docx")
        context = { 'code_snippet' : Listing(self.genCode_snippet) , 'answers' : Listing(cgenerator.getAnswers()) }
        doc.render(context)
        doc.save("generated_doc.docx")

gui = GUI()
gui.display()

