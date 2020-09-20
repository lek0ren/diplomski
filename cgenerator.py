from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
import string
import random
import re
from  parser import prettify


class CGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.allVariables = []

    def generateC(self):
        tree = ElementTree.parse(self.filename)

        root = tree.getroot()
        
        randNum = random.randint(0, len(root[0]))

        

        

        tree = ElementTree.ElementTree(root[randNum])
        #print(prettify(tree.getroot()))

        lastPadding = 0
        curlyBracket = ''
        padding = 0
        pandingBrackets = []
        doWhilelines = dict()

        code_snippet = ''

        #printing in c
        for elem in tree.iter():
            lastPadding = padding
            if elem.tag == 'instruction' or elem.tag == 'instruction' or elem.tag == 'if':
                padding = int(elem.attrib['depth'])


                if padding > lastPadding:
                    curlyBracket = '{'
                    print( '\t' * (padding - 1) + curlyBracket)
                    code_snippet += '\t' * (padding - 1) + curlyBracket + '\r\n'
                    pandingBrackets.append('}')
                elif padding < lastPadding:
                    if doWhilelines.get(padding) is not None:
                        print('\t' * padding + doWhilelines[padding])
                        code_snippet += '\t' * padding + doWhilelines[padding] + '\r\n'
                    curlyBracket = '}'
                else:
                    curlyBracket = ''

                if curlyBracket == '}':
                    if doWhilelines.get(padding) is not None:
                        doWhilelines.pop(padding)
                    else:
                        print( '\t' * (lastPadding -  1) + '}')
                        code_snippet += '\t' * (lastPadding -  1) + '}' +  '\r\n' 
                        pandingBrackets.pop()
                
            #instruction
            if elem.tag == 'instruction':
                
                print( '\t' * padding + f"{elem.attrib['var1']} = {elem.attrib['var2']};")
                code_snippet += '\t' * padding + f"{elem.attrib['var1']} = {elem.attrib['var2']};" +  '\r\n' 
            
            if elem.tag == 'loop':
                #for loop
                if elem.attrib['type'] == 'for':
                    print( '\t' * padding + f"for({elem.attrib['iterVar']} = {elem.attrib['iterVal']}; {elem.attrib['iterVar']} { '<' if elem.attrib['inc'] == '++' else '>='} {elem.attrib['endVar']}; {elem.attrib['iterVar']}{elem.attrib['inc']})")
                    code_snippet += '\t' * padding + f"for({elem.attrib['iterVar']} = {elem.attrib['iterVal']}; {elem.attrib['iterVar']} { '<' if elem.attrib['inc'] == '++' else '>='} {elem.attrib['endVar']}; {elem.attrib['iterVar']}{elem.attrib['inc']})" +  '\r\n' 

                #repeat loop
                if elem.attrib['type'] == 'repeat':
                    print(padding * '\t' + "do")
                    code_snippet += padding * '\t' + "do" +  '\r\n' 
                    doWhilelines[padding] = f"}} while({elem.attrib['iterVar']} {elem.attrib['op']} {elem.attrib['endVar']});"
                    #pandingBrackets.pop()
                #while loop
                if elem.attrib['type'] == 'while':
                    print( '\t' * padding + f"while({elem.attrib['condition']})")
                    code_snippet += '\t' * padding + f"while({elem.attrib['condition']})" +  '\r\n' 

            




            if elem.tag == 'if':
                print( '\t' * padding + f"if({elem.attrib['condition']})")
                code_snippet += '\t' * padding + f"if({elem.attrib['condition']})" +  '\r\n' 


        if doWhilelines.get(0) is not None:
            print(doWhilelines[0])
            code_snippet += doWhilelines[0] + '\r\n'
            pandingBrackets.pop()

        for idx,bracket in enumerate(pandingBrackets):
            print((len(pandingBrackets) - 1 - idx) * '\t' + bracket)
            code_snippet += (len(pandingBrackets) - 1 - idx) * '\t' + bracket +  '\r\n' 

        print('Answer:\t' + tree.getroot().attrib['answer'])
        