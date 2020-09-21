from cgenerator import CGenerator 
from parser import Parser
import tkinter as tk
from tkinter import Button

'''
parser = Parser('textZadatka.txt')
parser.parse()
print("Writing to file")
parser.appendToFile()

'''

window = tk.Tk()
cgenerator = CGenerator('zadaci/sviZadaci.xml')
cgenerator.generateC()


'''
btn=Button(window, text="This is Button widget", fg='blue')
btn.place(x=80, y=100)
window.title('Slozenost algoritma')
window.geometry("800x600+10+20")
window.mainloop()'''