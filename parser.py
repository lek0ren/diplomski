import re
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
import string
import random

inpupFile = open("zadaci/textZadatka.txt", "r")


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def extractVariables(allVariables,variables):
    """Return a dictionary of all variables extracted from a string
    """
    
    splitedVariables = re.split(r'[\s\[\]+\-\\*/\d]+',variables)
    for variable in splitedVariables:
        if not variable.isdigit() and variable != '' and variable != 'true' and variable != 'false':
            if not variable in allVariables:
                allVariables[variable] = ''
    return allVariables




def shuffleNames(allVariables):
    """Returns new variable names
    """
    usedLetters = set()
    for variable in allVariables:
        randomLetter = random.choice(string.ascii_lowercase) 
        while randomLetter == variable or randomLetter in usedLetters:
            randomLetter = random.choice(string.ascii_lowercase)
        usedLetters.add(randomLetter)
        allVariables[variable]=randomLetter
    
    return allVariables

currentScope = Element("program")
allScopes = [currentScope]
allVariables = dict()

foundBegin = False
startedLoop = False
numberOfLoopLines = 0


for line in inpupFile:
    print(line)

    #search for for loop
    matched = re.search(r'for (?P<iterVar>\w+)( *|):=( *|)(?P<iterVal>.+?(?= to| downto))( +|)(?P<inc>to|downto)( +|)(?P<endVar>.+?(?= do))',line)
    if matched is not None:
        

        print(f"c for({matched.group('iterVar')} = {matched.group('iterVal')};{matched.group('iterVar')} < {matched.group('endVar')};{matched.group('iterVar')}{ '++' if matched.group('inc') == 'to' else '--'})")
        top = SubElement(currentScope,"loop",{'type':'for', 'iterVal':matched.group('iterVal'), 'iterVar':matched.group('iterVar'), 'endVar':matched.group('endVar'), 'inc': '++' if matched.group('inc') == 'to' else '--'})
        
        allScopes.append(top)
        currentScope = top

        allVariables = extractVariables(allVariables,matched.group('iterVal'))
        allVariables = extractVariables(allVariables,matched.group('iterVar'))
        allVariables = extractVariables(allVariables,matched.group('endVar'))

        
        foundBegin = re.search(r'begin',line) is not None
        startedLoop = not foundBegin
        numberOfLoopLines = 0

        print(prettify(top))

    #search for instruction
    matched = re.search(r'(?P<var1>(?=[^\s]+).+?(?=:=))( *|):=( *|)(?P<var2>.+?(?=;))',line)
    if matched is not None:

        print(f"c {matched.group('var1')} = {matched.group('var2')};") 
        top = SubElement(currentScope,"instruction",{'var1':matched.group('var1'), 'var2':matched.group('var2')})


        allVariables = extractVariables(allVariables,matched.group('var1'))
        allVariables = extractVariables(allVariables,matched.group('var2'))
    

    #search for end
    matched = re.search(r'[eE]nd',line)
    if matched is not None:
        print(f"1end of scope for {currentScope}")
        currentScope = allScopes.pop()

    #search for begin
    matched = re.search(r'[b|B]egin',line)
    if matched is not None:
        startedLoop = True
        foundBegin = True
    

    #search for repeat
    matched = re.search(r'[Rr]epeat',line)
    if matched is not None:
        print(f'c do')
        top = SubElement(currentScope,"loop",{'type':'repeat'})
        
        allScopes.append(top)
        currentScope = top

        foundBegin = True
        startedLoop = True
        numberOfLoopLines = 2

    #search for until
    matched = re.search(r'[Uu]ntil (?P<iterVar>.+?(?==|>|<|>=|<=|<>))(?P<op>=|>|<|>=|<=|<>])(?P<endVar>.+)',line)
    if matched is not None:
        print(f"c while({matched.group('iterVar')} {matched.group('op')} {matched.group('endVar')})")
        currentScope.attrib['iterVar']=matched.group('iterVar')
        currentScope.attrib['op']=matched.group('op')

        if matched.group('op') == "=":
                currentScope.attrib['op']='=='
        if matched.group('op') == '<>':
                currentScope.attrib['op']='!='

        currentScope.attrib['endVar']=matched.group('endVar')

        currentScope = allScopes.pop()


    #handeling of one line for loop
    if not foundBegin and numberOfLoopLines == 1:
        print(f"3end of scope for {currentScope}")
        currentScope = allScopes.pop()
        startedLoop = False
        
    if startedLoop:
        numberOfLoopLines+=1

print(prettify(allScopes[0]))
print(allVariables)


allVariables = shuffleNames(allVariables)

print(allVariables)

tree = ElementTree.ElementTree(allScopes[0])

for elem in tree.iter():
    if elem.tag == 'instruction':
        elem.attrib['var1']=allVariables[elem.attrib['var1']]


print(prettify(tree.getroot()))
