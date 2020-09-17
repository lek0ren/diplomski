from docxtpl import DocxTemplate, Listing
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
    print(splitedVariables)
    for variable in splitedVariables:
        if variable.islower() and variable != '' and variable != 'true' and variable != 'false':
            if not variable in allVariables:
                allVariables[variable] = ''
    return allVariables



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
        allVariables[variable]=randomLetter
    
    return allVariables



currentScope = Element("program")
allScopes = [currentScope]
allVariables = dict()

foundBegin = False
startedLoop = False
numberOfLoopLines = 0
depth = 0


for line in inpupFile:
    print(line)

    #search for for loop
    matched = re.search(r'for (?P<iterVar>\w+)( *|):=( *|)(?P<iterVal>.+?(?= to| downto))( +|)(?P<inc>to|downto)( +|)(?P<endVar>.+?(?= do))',line)
    if matched is not None:
        

        print(f"c for({matched.group('iterVar')} = {matched.group('iterVal')};{matched.group('iterVar')} < {matched.group('endVar')};{matched.group('iterVar')}{ '++' if matched.group('inc') == 'to' else '--'})")
        top = SubElement(currentScope,"loop",{'type':'for', 'iterVal':matched.group('iterVal'), 'iterVar':matched.group('iterVar'), 'endVar':matched.group('endVar'), 'inc': '++' if matched.group('inc') == 'to' else '--', 'depth': str(depth)})
        depth += 1
        allScopes.append(top)
        currentScope = top

        allVariables = extractVariables(allVariables,matched.group('iterVal'))
        allVariables = extractVariables(allVariables,matched.group('iterVar'))
        allVariables = extractVariables(allVariables,matched.group('endVar'))

        
        #foundBegin = re.search(r'begin',line) is not None
        #startedLoop = not foundBegin
        #numberOfLoopLines = 0

        print(prettify(top))

    #search for instruction
    matched = re.search(r'(?P<var1>(?=[^\s]+).+?(?=:=))( *|):=( *|)(?P<var2>.+?(?=;))',line)
    if matched is not None:

        print(f"c {matched.group('var1')} = {matched.group('var2')};") 
        top = SubElement(currentScope,"instruction",{'var1':matched.group('var1'), 'var2':matched.group('var2'), 'depth': str(depth)})


        allVariables = extractVariables(allVariables,matched.group('var1'))
        allVariables = extractVariables(allVariables,matched.group('var2'))
    

    #search for end
    matched = re.search(r'[eE]nd',line)
    if matched is not None:
        print(f"1end of scope for {currentScope}")
        currentScope = allScopes.pop()
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
        
        top = SubElement(currentScope,"loop",{'type':'repeat', 'depth': str(depth)})
        depth += 1
        allScopes.append(top)
        currentScope = top

        #foundBegin = True
        #startedLoop = True
        numberOfLoopLines = 2

    #search for until
    matched = re.search(r'[Uu]ntil (?P<iterVar>.+?(?==|>|<|>=|<=|<>))(?P<op>=|>|<|>=|<=|<>])(?P<endVar>.+)',line)
    if matched is not None:
        depth -= 1
        print(f"c while({matched.group('iterVar')} {matched.group('op')} {matched.group('endVar')})")
        currentScope.attrib['iterVar']=matched.group('iterVar')
        currentScope.attrib['op']=matched.group('op')

        if matched.group('op') == "=":
                currentScope.attrib['op']='=='
        if matched.group('op') == '<>':
                currentScope.attrib['op']='!='

        currentScope.attrib['endVar']=matched.group('endVar')

        currentScope = allScopes.pop()


    #search for while loop
    matched = re.search(r'[wW]hile( +|)(?P<condition>.+?(?=\sdo))',line)
    if matched is not None:
        top = SubElement(currentScope,"loop",{'type':'while', 'condition':matched.group('condition'), 'depth': str(depth)})
        depth += 1
        allScopes.append(top)
        currentScope = top


    #search for if statement
    matched = re.search(r'[iI]f( +|)(?P<condition>(.+?(?=\sthen)))',line)
    if matched is not None:
        top = SubElement(currentScope,"if",{'condition':matched.group('condition'), 'depth': str(depth)})
        depth += 1
        allScopes.append(top)
        currentScope = top

    #handeling of one line for loop
    if not foundBegin and numberOfLoopLines == 1:
        print(f"3end of scope for {currentScope}")
        currentScope = allScopes.pop()
        #startedLoop = False
        
    if startedLoop:
        numberOfLoopLines+=1

print(prettify(allScopes[0]))
print(allVariables)


allVariables = shuffleNames(allVariables)

print(allVariables)

tree = ElementTree.ElementTree(allScopes[0])

compiledRegexLetters = dict()

for letter in allVariables:
    compiledRegexLetters[letter] = re.compile('\b(?!false|true)\b' + letter)

for elem in tree.iter():
    if elem.tag == 'instruction':
        for var in allVariables:
            elem.attrib['var1'] = re.sub(var,allVariables[var],elem.attrib['var1'])
            if elem.attrib['var2'] != 'true' and elem.attrib['var2'] != 'false':
                elem.attrib['var2'] = re.sub(var,allVariables[var],elem.attrib['var2'])
            else:
                elem.attrib['var2'] = re.sub('true','1',elem.attrib['var2'])
                elem.attrib['var2'] = re.sub('false','0',elem.attrib['var2'])
        
    if elem.tag == 'loop':
        if elem.attrib['type'] != 'while':
            for var in allVariables:
                elem.attrib['endVar'] = re.sub(var,allVariables[var],elem.attrib['endVar'])
                elem.attrib['iterVar']=re.sub(var,allVariables[var],elem.attrib['iterVar'])
            if(elem.attrib['type'] == 'for'):
                for var in allVariables:
                    elem.attrib['iterVal'] = re.sub(var,allVariables[var],elem.attrib['iterVal'])
        else:
            elem.attrib['condition'] = re.sub('and','&&',elem.attrib['condition'])
            elem.attrib['condition'] = re.sub('or','||',elem.attrib['condition'])
            elem.attrib['condition'] = re.sub(' =',' ==',elem.attrib['condition'])
            elem.attrib['condition'] = re.sub('<>','!=',elem.attrib['condition'])
            for var in allVariables:
                elem.attrib['condition'] = re.sub(var,allVariables[var],elem.attrib['condition'])


    if elem.tag == 'if':
        elem.attrib['condition'] = re.sub('and','&&',elem.attrib['condition'])
        elem.attrib['condition'] = re.sub('or','||',elem.attrib['condition'])
        elem.attrib['condition'] = re.sub(' =',' ==',elem.attrib['condition'])
        elem.attrib['condition'] = re.sub('<>','!=',elem.attrib['condition'])
        for var in allVariables:
                elem.attrib['condition'] = re.sub(var,allVariables[var],elem.attrib['condition'])
            

print(prettify(tree.getroot()))

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
            if(doWhilelines[padding]):
                print('\t' * padding + doWhilelines[padding])
                code_snippet += '\t' * padding + doWhilelines[padding] + '\r\n'
            curlyBracket = '}'
        else:
            curlyBracket = ''
        
    #instruction
    if elem.tag == 'instruction':
        
        print( '\t' * padding + f"{elem.attrib['var1']} = {elem.attrib['var2']};")
        code_snippet += '\t' * padding + f"{elem.attrib['var1']} = {elem.attrib['var2']};" +  '\r\n' 
    
    if elem.tag == 'loop':
        #for loop
        if elem.attrib['type'] == 'for':
            print( '\t' * padding + f"for({elem.attrib['iterVar']} = {elem.attrib['iterVal']};{elem.attrib['iterVar']} { '<' if elem.attrib['inc'] == '++' else '>='} {elem.attrib['endVar']};{elem.attrib['iterVar']}{elem.attrib['inc']})")
            code_snippet += '\t' * padding + f"for({elem.attrib['iterVar']} = {elem.attrib['iterVal']};{elem.attrib['iterVar']} { '<' if elem.attrib['inc'] == '++' else '>='} {elem.attrib['endVar']};{elem.attrib['iterVar']}{elem.attrib['inc']})" +  '\r\n' 

        #repeat loop
        if elem.attrib['type'] == 'repeat':
            print(padding * '\t' + "do")
            code_snippet += padding * '\t' + "do" +  '\r\n' 
            doWhilelines[padding] = f"}} while({elem.attrib['iterVar']} {elem.attrib['op']} {elem.attrib['endVar']});"
            pandingBrackets.pop()
        #while loop
        if elem.attrib['type'] == 'while':
            print( '\t' * padding + f"while({elem.attrib['condition']})")
            code_snippet += '\t' * padding + f"while({elem.attrib['condition']})" +  '\r\n' 

    if elem.tag == 'if':
        print( '\t' * padding + f"if({elem.attrib['condition']})")
        code_snippet += '\t' * padding + f"if({elem.attrib['condition']})" +  '\r\n' 


    if curlyBracket == '}':
        if(doWhilelines[padding]):
            doWhilelines.pop(padding)
        else:
            print( '\t' * padding + '}')
            code_snippet += '\t' * padding + '}' +  '\r\n' 
            pandingBrackets.pop()

for idx,bracket in enumerate(pandingBrackets):
    print((len(pandingBrackets) - 1 - idx) * '\t' + '}')
    code_snippet += (len(pandingBrackets) - 1 - idx) * '\t' + '}' +  '\r\n' 



doc = DocxTemplate("templates/one_program.docx")
context = { 'code_snippet' : Listing(code_snippet) }
doc.render(context)
doc.save("generated_doc.docx")
