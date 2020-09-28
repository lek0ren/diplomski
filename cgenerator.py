from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
import string
import random
import re
from  parser import prettify
import json


def shuffleNames(allVariables):
    """Returns new variable names
    """
    usedLetters = set()
    for var in allVariables:
        usedLetters.add(var)

        
    for variable in allVariables:
        randomLetter = random.choice(string.ascii_lowercase) 
        while randomLetter == variable or randomLetter in usedLetters:
            randomLetter = random.choice(string.ascii_lowercase)
        usedLetters.add(randomLetter)
        if variable == 'n':
            allVariables[variable] = 'n'
        else:
            allVariables[variable]=randomLetter
    
    return allVariables

class CGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.allVariables = []
        self.program = None
        self.answers = ''
        self.allAnswers = ["n","n * log(n)","n^2","n^2 * log(n)","n^3","n!","log(n!)","log(n)","sqrt(n)", "n^3/2"]

    def setProgram(self, program):
        self.program = program

    def getAnswers(self):
            return self.answers

    def setRandomProgram(self):
        tree = ElementTree.parse(self.filename)
        root = tree.getroot()   
        randNum = random.randint(0, len(root) - 1)
        self.program = root[randNum]

    def generateC(self):
        self.answers = ''

        tree = ElementTree.ElementTree(self.program)

        tree.getroot().attrib['variables'] = tree.getroot().attrib['variables'].replace("'", '"').replace('u"', '"')

        allVariables = json.loads(tree.getroot().attrib['variables'])
        
        allVariables = shuffleNames(allVariables)


        for elem in tree.getroot().iter():
            if elem.tag == 'instruction':
                for var in allVariables:
                    elem.attrib['var1'] = re.sub(var,allVariables[var],elem.attrib['var1'])
                    if elem.attrib['var2'] != 'true' and elem.attrib['var2'] != 'false':
                        elem.attrib['var2'] = re.sub('div','/',elem.attrib['var2'])
                        elem.attrib['var2'] = re.sub('mod','%',elem.attrib['var2'])
                        elem.attrib['var2'] = re.sub(var,allVariables[var],elem.attrib['var2'])
                    else:
                        elem.attrib['var2'] = re.sub('true','1',elem.attrib['var2'])
                        elem.attrib['var2'] = re.sub('false','0',elem.attrib['var2'])

            if elem.tag == 'loop':
                if elem.attrib['type'] == 'while':
                    elem.attrib['endVar'] = re.sub('and','&&',elem.attrib['endVar'])
                    elem.attrib['endVar'] = re.sub('or','||',elem.attrib['endVar'])
                    elem.attrib['endVar'] = re.sub(' =',' ==',elem.attrib['endVar'])
                    elem.attrib['endVar'] = re.sub('<>','!=',elem.attrib['endVar'])
                    elem.attrib['condition'] = re.sub('and','&&',elem.attrib['condition'])
                    elem.attrib['condition'] = re.sub('or','||',elem.attrib['condition'])
                    elem.attrib['condition'] = re.sub(' =',' ==',elem.attrib['condition'])
                    elem.attrib['condition'] = re.sub('<>','!=',elem.attrib['condition'])


                for var in allVariables:
                    elem.attrib['endVar'] = re.sub(var,allVariables[var],elem.attrib['endVar'])
                    elem.attrib['iterVar']=re.sub(var,allVariables[var],elem.attrib['iterVar'])
                    if 'condition' in elem.attrib:
                        elem.attrib['condition'] = re.sub(var,allVariables[var],elem.attrib['condition'])
                if(elem.attrib['type'] == 'for'):
                    for var in allVariables:
                        elem.attrib['iterVal'] = re.sub(var,allVariables[var],elem.attrib['iterVal'])
                
                
                    


            if elem.tag == 'if':
                elem.attrib['condition'] = re.sub('and','&&',elem.attrib['condition'])
                elem.attrib['condition'] = re.sub('or','||',elem.attrib['condition'])
                elem.attrib['condition'] = re.sub(' =',' ==',elem.attrib['condition'])
                elem.attrib['condition'] = re.sub('<>','!=',elem.attrib['condition'])
                for var in allVariables:
                        elem.attrib['condition'] = re.sub(var,allVariables[var],elem.attrib['condition'])
                    


        

        

        
        #print(prettify(tree.getroot()))

        lastPadding = 0
        curlyBracket = ''
        padding = 0
        pandingBrackets = []
        doWhilelines = dict()

        code_snippet = ''
        loopIteration = ''
        whileLoopIteration = ''

        #printing in c
        for elem in tree.iter():
            lastPadding = padding
            if elem.tag != 'program':
                padding = int(elem.attrib['depth'])


            if padding > lastPadding:
                curlyBracket = '{'
                print( '\t' * (padding - 1) + curlyBracket)
                code_snippet += '    ' * (padding - 1) + curlyBracket + '\r\n'
                if loopIteration != '':
                    print( '\t' * padding + loopIteration)
                    code_snippet += '    ' * padding + loopIteration +  '\r\n'
                    loopIteration = ''
                pandingBrackets.append('}')
            elif padding < lastPadding:
                if doWhilelines.get(padding) is not None:
                    print('\t' * padding + doWhilelines[padding])
                    code_snippet += '    ' * padding + doWhilelines[padding] + '\r\n'
                curlyBracket = '}'
            else:
                curlyBracket = ''

            if curlyBracket == '}':
                if doWhilelines.get(padding) is not None:
                    doWhilelines.pop(padding)
                else:
                    print( '\t' * (lastPadding -  1) + '}')
                    code_snippet += '    ' * (lastPadding -  1) + '}' +  '\r\n' 
                    pandingBrackets.pop()
                    if len(pandingBrackets) > 0 and padding == 0:
                        print('}')
                        code_snippet += '}' +  '\r\n' 
                        pandingBrackets.pop()
                
            #instruction
            if elem.tag == 'instruction':
                if 'whileLoop' in elem.attrib:
                    whileLoopIteration = f"{elem.attrib['var1']} = {elem.attrib['var2']};"
                else:
                    print( '\t' * padding + f"{elem.attrib['var1']} = {elem.attrib['var2']};")
                    code_snippet += '    ' * padding + f"{elem.attrib['var1']} = {elem.attrib['var2']};" +  '\r\n' 
            
            if elem.tag == 'loop':
                #for loop
                if elem.attrib['type'] == 'for':
                    if random.randint(0,2) == 0:
                        print( '\t' * padding + f"for({elem.attrib['iterVar']} = {elem.attrib['iterVal']}; {elem.attrib['iterVar']} { '<' if elem.attrib['inc'] == '++' else '>='} {elem.attrib['endVar']}; {elem.attrib['iterVar']}{elem.attrib['inc']})")
                        code_snippet += '    ' * padding + f"for({elem.attrib['iterVar']} = {elem.attrib['iterVal']}; {elem.attrib['iterVar']} { '<' if elem.attrib['inc'] == '++' else '>='} {elem.attrib['endVar']}; {elem.attrib['iterVar']}{elem.attrib['inc']})" +  '\r\n' 
                    else: 
                        print( '\t' * padding + f"{elem.attrib['iterVar']} = {elem.attrib['iterVal']};")
                        code_snippet += '    ' * padding + f"{elem.attrib['iterVar']} = {elem.attrib['iterVal']};" +  '\r\n'
                        print( '\t' * padding + f"while({elem.attrib['iterVar']} { '<' if elem.attrib['inc'] == '++' else '>='} {elem.attrib['endVar']})")
                        code_snippet += '    ' * padding + f"while({elem.attrib['iterVar']} { '<' if elem.attrib['inc'] == '++' else '>='} {elem.attrib['endVar']})" +  '\r\n'
                        loopIteration = f"{elem.attrib['iterVar']}{elem.attrib['inc']};" 


                #repeat loop
                if elem.attrib['type'] == 'repeat':
                    print(padding * '\t' + "do")
                    code_snippet += padding * '    ' + "do" +  '\r\n' 
                    doWhilelines[padding] = f"}} while({elem.attrib['iterVar']} {elem.attrib['op']} {elem.attrib['endVar']});"
                    #pandingBrackets.pop()
                #while loop
                if elem.attrib['type'] == 'while':
                    if random.randint(0,2) == 0 or 'inc' not in elem.attrib: 
                        print('\t' * padding + whileLoopIteration)
                        code_snippet += '    ' * padding + whileLoopIteration + '\r\n'
                        print( '\t' * padding + f"while({elem.attrib['condition']})")
                        code_snippet += '    ' * padding + f"while({elem.attrib['condition']})" +  '\r\n' 
                    else:
                        print( '\t' * padding + f"for({whileLoopIteration} {elem.attrib['condition']}; {elem.attrib['iterVar']}{elem.attrib['inc']})")
                        code_snippet += '    ' * padding + f"for({whileLoopIteration} {elem.attrib['condition']} ; {elem.attrib['iterVar']}{elem.attrib['inc']})" +  '\r\n' 
            




            if elem.tag == 'if':
                print( '\t' * padding + f"if({elem.attrib['condition']})")
                code_snippet += '    ' * padding + f"if({elem.attrib['condition']})" +  '\r\n' 

            if elem.tag == 'else':
                print( '\t' * padding + f"else")
                code_snippet += '    ' * padding + f"else" +  '\r\n' 


        for doWhile in  doWhilelines:
            print('\t' * doWhile + doWhilelines[doWhile])
            code_snippet += '    ' * doWhile + doWhilelines[doWhile] + '\r\n'
            pandingBrackets.pop()

        for idx,bracket in enumerate(pandingBrackets):
            print((len(pandingBrackets) - 1 - idx) * '\t' + bracket)
            code_snippet += (len(pandingBrackets) - 1 - idx) * '    ' + bracket +  '\r\n' 

        print('Answer:\t' + tree.getroot().attrib['answer'])
        print('Wrong:\t' + tree.getroot().attrib['wrong'])

        self.answers += 'Tacan odgovor:\t' + tree.getroot().attrib['answer'] +  '\r\n' 
        self.answers += 'Pogresan odgovor:\t' + tree.getroot().attrib['wrong'] +  '\r\n' 

        falseAnswer = self.allAnswers[random.randint(0, len(self.allAnswers)) - 1]
        while falseAnswer == tree.getroot().attrib['wrong'] or falseAnswer == tree.getroot().attrib['answer']:
            falseAnswer = self.allAnswers[random.randint(0, len(self.allAnswers) - 1)]
        
        self.answers += 'Pogresan odgovor:\t' + falseAnswer +  '\r\n' 

        return code_snippet
        