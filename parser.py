from docxtpl import DocxTemplate, Listing
import re
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
import string
import random




def prettify(elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")




class Parser:
    def __init__(self, filename):
        self.filename = filename
        self.currentScope = Element("program")
        self.allScopes = [self.currentScope]
        self.allVariables = dict()


    def resetAllScopes(self):
        self.currentScope = Element("program")
        self.allScopes = [self.currentScope]

    def getCurrentProgram(self):
        return self.allScopes[0]

    def parse(self):
        inpupFile = open("zadaci/" + self.filename, "r")

        '''
        foundBegin = False
        startedLoop = False
        '''
        numberOfLoops = 0
        depth = 0


        

        for line in inpupFile:
            print(line)

            #search for for loop
            matched = re.search(r'for (?P<iterVar>\w+)( *|):=( *|)(?P<iterVal>.+?(?= to| downto))( +|)(?P<inc>to|downto)( +|)(?P<endVar>.+?(?= do))',line)
            if matched is not None:
                
                
                print(f"c for({matched.group('iterVar')} = {matched.group('iterVal')};{matched.group('iterVar')} < {matched.group('endVar')};{matched.group('iterVar')}{ '++' if matched.group('inc') == 'to' else '--'})")
                top = SubElement(self.currentScope,"loop",{'type':'for', 'iterVal':matched.group('iterVal'), 'iterVar':matched.group('iterVar'), 'endVar':matched.group('endVar'), 'inc': '++' if matched.group('inc') == 'to' else '--', 'depth': str(depth)})
                depth += 1
                self.allScopes.append(top)
                self.currentScope = top

                self.allVariables = self.extractVariables(matched.group('iterVal'))
                self.allVariables = self.extractVariables(matched.group('iterVar'))
                self.allVariables = self.extractVariables(matched.group('endVar'))

                numberOfLoops += 1
                #foundBegin = re.search(r'begin',line) is not None
                #startedLoop = not foundBegin
                #numberOfLoopLines = 0

                print(prettify(top))

            #search for instruction
            matched = re.search(r'(?P<var1>(?=[^\s]+).+?(?=:=))( *|):=( *|)(?P<var2>.+?(?=;))',line)
            if matched is not None:
                var1 = re.sub(r' ','',matched.group('var1'))
                print(f"c {var1} = {matched.group('var2')};") 
                top = SubElement(self.currentScope,"instruction",{'var1':var1, 'var2':matched.group('var2'), 'depth': str(depth)})
 
                if 'type' in self.currentScope.attrib and self.currentScope.attrib['type'] == 'while' and self.currentScope.attrib['iterVar'] == var1:
                    match = re.search(r'.*(?P<op>\+|-)', matched.group('var2'))
                    if match is not None:
                        self.currentScope.attrib['inc'] = '++' if match.group('op') == '+' else '--'
                        root = ElementTree.ElementTree(self.allScopes[0])
                        for elem in root.iter():
                            if 'var1' in elem.attrib:
                                    print(elem.get('var1') + ' = ' + self.currentScope.attrib['iterVar'] + '  ;  |' + elem.attrib['var2'] + '| =  |' +  matched.group('var2') + '|')
                                    if elem.get('var1') == self.currentScope.attrib['iterVar'] and elem.attrib['var2'] != matched.group('var2'):
                                        self.currentScope.attrib['iterVal'] = elem.attrib['var2']
                                        elem.attrib['whileLoop'] = 'true'

                self.allVariables = self.extractVariables(var1)
                self.allVariables = self.extractVariables(matched.group('var2'))
            

            #search for end
            matched = re.search(r'[eE]nd',line)
            if matched is not None:
                print(self.allScopes)
                self.allScopes.pop()
                self.currentScope = self.allScopes[-1]
                depth -= 1

            #search for begin
            matched = re.search(r'[b|B]egin',line)
            #if matched is not None:
                #startedLoop = True
                #foundBegin = True
            

            #search for repeat
            matched = re.search(r'[Rr]epeat',line)
            if matched is not None:
                print(f'c do')
                numberOfLoops += 1
                top = SubElement(self.currentScope,"loop",{'type':'repeat', 'depth': str(depth)})
                depth += 1
                self.allScopes.append(top)
                self.currentScope = top

                #foundBegin = True
                #startedLoop = True
                

            #search for until
            matched = re.search(r'[Uu]ntil (?P<iterVar>.+?(?==|>=|<=|<>|>|<))(?P<op>=|>=|<=|<>|>|<)(?P<endVar>.+(?=;))',line)
            if matched is not None:
                depth -= 1
                print(f"c while({matched.group('iterVar')} {matched.group('op')} {matched.group('endVar')})")
                self.currentScope.attrib['iterVar']=matched.group('iterVar')
                self.currentScope.attrib['op']=matched.group('op')

                if matched.group('op') == "=":
                        self.currentScope.attrib['op']='=='
                if matched.group('op') == '<>':
                        self.currentScope.attrib['op']='!='

                self.currentScope.attrib['endVar']=matched.group('endVar')

                self.allScopes.pop()
                self.currentScope = self.allScopes[-1]


            #search for while loop
            matched = re.search(r'[wW]hile( +|)(?P<iterVar>.+?(?==|>=|<=|<>|>|<))(?P<op>=|>=|<=|<>|>|<)\s*(?P<endVar>.+(?=\s*do))(\s*do)',line)
            if matched is not None:
                condition = matched.group('iterVar') + matched.group('op') + matched.group('endVar')
                iterVar = re.sub(r'\(| ','',matched.group('iterVar'))
                endVar = re.sub(r'\)','',matched.group('endVar'))
                top = SubElement(self.currentScope,"loop",{'type':'while', 'op':matched.group('op'),'iterVar':iterVar,'endVar': endVar, 'condition': condition,'depth': str(depth)})
                depth += 1
                self.allScopes.append(top)
                self.currentScope = top
                numberOfLoops += 1

            #search for if statement
            matched = re.search(r'[iI]f( +|)(?P<condition>(.+?(?=\sthen)))',line)
            if matched is not None:
                print(self.currentScope)
                top = SubElement(self.currentScope,"if",{'condition':matched.group('condition'), 'depth': str(depth)})
                depth += 1
                self.allScopes.append(top)
                self.currentScope = top
                print(self.currentScope)

            #search for if statement
            matched = re.search(r'else',line)
            if matched is not None:
                top = SubElement(self.currentScope,"else", {'depth': str(depth)})
                depth += 1
                self.allScopes.append(top)
                self.currentScope = top

            #search for answer
            matched = re.search(r'answer:\s*(?P<answer>.+)',line)
            if matched is not None:
                self.allScopes[0].attrib['answer'] = matched.group('answer')
            '''
            #handeling of one line for loop
            if not foundBegin and numberOfLoopLines == 1:
                print(f"3end of scope for {self.currentScope}")
                self.currentScope = self.allScopes.pop()
                #startedLoop = False
              '''  
            
        if self.allScopes[0].attrib['answer'] == 'n^' + str(numberOfLoops):
            self.allScopes[0].attrib['wrong'] = 'n' + f"{'^' + str(numberOfLoops - 1) if numberOfLoops != 1 and numberOfLoops != 2 else ''}" + ' * log(n)'
        else:
            self.allScopes[0].attrib['wrong'] = 'n^' + str(numberOfLoops)
        print(self.allVariables)
        self.allScopes[0].attrib['variables']= str(self.allVariables)
        print(prettify(self.allScopes[0]))
        self.currentScope = self.allScopes[0]

        





    def extractVariables(self,variables):
        """Return a dictionary of all variables extracted from a string
        """
        
        splitedVariables = re.split(r'[\s\[\]+\-\\*/\d]+',variables)
        print(splitedVariables)
        for variable in splitedVariables:
            if variable.islower() and variable != '' and variable != 'true' and variable != 'false' and variable != 'div' and variable != 'mod':
                if not variable in self.allVariables:
                    self.allVariables[variable] = ''
        return self.allVariables


    def appendToFile(self):
        tree = ElementTree.parse("zadaci/sviZadaci.xml")
        root = tree.getroot()
        #self.prettify(root)
        #root = ElementTree.Element("all-programs")
        #print(self.prettify(root))
        root.insert(0,self.allScopes[0])

        mydata = ElementTree.tostring(root,'unicode', 'xml')
        myfile = open("zadaci/sviZadaci.xml", "w")
        myfile.write(mydata)
        myfile.close()





'''
doc = DocxTemplate("templates/one_program.docx")
context = { 'code_snippet' : Listing(code_snippet) }
doc.render(context)
doc.save("generated_doc.docx")
'''