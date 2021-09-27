# This converts the syntactic tree to the final 3AC "Machine Code" equivalent

# Used on if/for are relative line referencing
# Relative line referencing:
# __X__, will be switched to X+currentLine
# ==X==, will be switched to currentLine-X

# Temporary variables used by the code should be from address 2000 onwards
TEMP_VAR_OFFSET = 2000

# This will build the code related to each expression based on it's type
def build_exp(exp):
    child = exp['children'][0]
    if child['type'] == 'declaration' or child['type'] == 'assigment':
        return build_declaration_assigment(child)
    if child['type'] == 'ifbloco':
        return build_ifblock(child)
    if child['type'] == 'operacao':
        return build_operacao(child)[1]
    if child['type'] == 'forloop':
        return build_forloop(child)

def build_ifblock(exp):
    
    # The if block has 3 parts
    # preop are the opperations made before the condition is tested
    preop = []
    # Code is the code run if the condition is true
    code = []
    # Jump is the part that "skips" the code if the condition is tested false
    jump = []
    
    for p in exp['children'][1]['children']:
        tcode = build_exp(p)
        code += tcode

    condition = exp['children'][0]['children'][0]['value']
    values = exp['children'][0]['children'][0]['children']

    # This will get the first value of the conditional
    # if this is a operation it will also get the operation code and add it to preop
    v1 = values[0]['value']
    if values[0]['type'] == "variavel":
        v1 = '$'+ str(symbol_table["variables"].index(values[0]['value']))
    elif values[0]['type'] == "operacao":
        v1, opcode = build_operacao(values[0])
        preop += opcode

    v2 = values[1]['value']
    if values[1]['type'] == "variavel":
        v2 = '$'+ str(symbol_table["variables"].index(values[0]['value']))
    elif values[1]['type'] == "operacao":
        v2, opcode = build_operacao(values[0])
        preop += opcode

    # Building the conditionals require knowing both values, the condition, and how much 
    # to jump in order to avoid the code if the condition is tested false
    jump = build_conditional(v1,v2,condition,len(code))
        
    return preop+jump+code

def build_conditional(v1,v2,condition,codelen):
    jump = []

    # Conditions have to be reversed, we only want to jump and skip
    # the code if it was tested false
    if condition == '==':
        jump = [
            f'&1 = {v1} - {v2}',
            f'jmpgz __{codelen+2}__ &1',
            f'jmplz __{codelen+1}__ &1']
    elif condition == '!=':
        jump = [
            f'&1 = {v1} - {v2}',
            f'jmpz __{codelen+1}__ &1']
    elif condition == '>=':
        jump = [
            f'&1 = {v1} - {v2}',
            f'jmplz __{codelen+1}__ &1']  
    elif condition =='<=':
        jump = [
            f'&1 = {v1} - {v2}',
            f'jmpgz __{codelen+1}__ &1']
    elif condition =='>':
        jump = [
            f'&1 = {v1} - {v2}',
            f'jmplz __{codelen+2}__ &1',
            f'jmpz __{codelen+1}__ &1']
    elif condition =='<':
        jump = [
            f'&1 = {v1} - {v2}',
            f'jmpgz __{codelen+2}__ &1',
            f'jmpz __{codelen+1}__ &1']
    return jump

# This function will build basic variable assignment
def build_declaration_assigment(exp):
    # This gets the variable Address based on the symbol table
    varReference = symbol_table["variables"].index(exp["value"])

    # If the variable was just created, the code will just assign 0 to it
    if len(exp['children']) == 0:
        return [f'${varReference} = 0']

    # The rest of this function will match the assigned value to either a value
    child = exp['children'][0]
    if child['type'] == 'valorNumerico':
        return [f'${varReference} = {child["value"]}']
    # an operation
    elif child['type'] == 'operacao':
        value, code = build_operacao(child,varReference)
        return code
    # or a variable
    elif child['type'] == 'variavel':
        return [f'${varReference} = ${symbol_table["variables"].index(child["value"])}']

def build_forloop(exp):
    # The for loop is build as follows:
    # pre-loop
    # condition testing
    # code
    # finalizer
    # jump to condition testing

    code = []

    # Build the pre-loop if it exists
    x = 0
    inicializador = []
    if exp['children'][x]['type'] == 'inicializador':
        inicializador = build_declaration_assigment(exp['children'][x]['children'][0])
        x += 1

    # Save the conditional tree to build later (it requires knowing the lenght of the code)
    conditionTree = exp['children'][x]
    x += 1

    # Build the end of the loop part
    finalizador = []
    if exp['children'][x]['type'] == 'finalizador':
        finalizador = build_exp(exp['children'][x])
        x += 1

    # Build the code executed in the loop
    block = []
    for p in exp['children'][x]['children']:
        tcode = build_exp(p)
        block += tcode

    # This has all the loop inside code
    tcode = block + finalizador

    # Now much like the 'if' we build the conditionals to skip the loop if they are tested false
    condition = conditionTree['children'][0]['value']
    values = conditionTree['children'][0]['children']
    preop = []
    v1 = values[0]['value']
    if values[0]['type'] == "variavel":
        v1 = '$'+ str(symbol_table["variables"].index(values[0]['value']))
    elif values[0]['type'] == "operacao":
        v1, opcode = build_operacao(values[0])
        preop += opcode

    v2 = values[1]['value']
    if values[1]['type'] == "variavel":
        v2 = '$'+ str(symbol_table["variables"].index(values[0]['value']))
    elif values[1]['type'] == "operacao":
        v2, opcode = build_operacao(values[0])
        preop += opcode


    conditionalCode = preop + build_conditional(v1,v2,condition,len(tcode)+2)

    # Add at the end of the loop we need the command to return to the start of the loop
    tcode += [f'&0 = =={len(tcode)+len(conditionalCode)}==']


    return (inicializador if inicializador else []) + conditionalCode+tcode

temp_block = 0

def increment_temp():
    global temp_block
    temp_block += 1
    temp_block = temp_block%48

# this function builds operation code in a recursive manner
def build_operacao(exp,result_variable = TEMP_VAR_OFFSET):
    # temporary variables are assigned in a cyclic order, this means we need a global variable
    # to control what will be the next temporary variable address
    global temp_block
    if result_variable == TEMP_VAR_OFFSET:
        result = temp_block+TEMP_VAR_OFFSET
        increment_temp()
    else:
        result = result_variable

    ## If the operation is a unary operation (x++)
    # not only the value has to be calculated but X also needs to be incremented
    if exp['value'] == 'unary':
        value, code = build_operacao(exp['children'][0],result_variable)
        variable = symbol_table["variables"].index(exp['children'][0]['children'][0]['value'])
        return value, code + [f'${variable} = {value}']

    result_code = []

    # This section will generate the code for any nested operations and get their temporary address
    # or get the raw value/variable address
    if exp['children'][0]['type'] == 'operacao':
        value1, code = build_operacao(exp['children'][0])
        result_code += code
    elif exp['children'][0]['type'] == 'variavel':
        value1 = f'${symbol_table["variables"].index(exp["children"][0]["value"])}'
    elif exp['children'][0]['type'] == 'valorNumerico':
        value1 = f'{exp["children"][0]["value"]}'

    if exp['children'][1]['type'] == 'operacao':
        value2, code = build_operacao(exp['children'][1])
        result_code += code
    elif exp['children'][1]['type'] == 'variavel':
        value2 = f'${symbol_table["variables"].index(exp["children"][1]["value"])}'
    elif exp['children'][1]['type'] == 'valorNumerico':
        value2 = f'{exp["children"][1]["value"]}'

    # once all the recursive operations have been transformed to code,
    # we append the initial operation at the end, with the values used
    result_code.append(f'${result} = {value1} {exp["value"]} {value2}')
    # This function not only returns the code but the temporary variable that the result was stored
    # Making it easy to use with recursion
    return f'${result}',result_code
    

import json
symbol_table = {}
program_tree = {}

with open('symbol_table.json','r') as file:
    symbol_table = json.loads(file.read())

with open('arvore.json','r') as file:
    program_tree = json.loads(file.read())
line = 0
finalcode = ''
for exp in program_tree['children']:
    for p in build_exp(exp):
        l = p
        # This section will change any relative line number to its absolute line number
        if '__' in l:
            idx = l.find('__')+2
            buffer = ''
            char = l[idx]
            x = 1
            while char != '_':
                buffer += char
                char = l[idx+x]
                x += 1
            code = int(buffer)
            l = l.replace(f'__{code}__',f'{code+line}')
        if '==' in l:
            idx = l.find('==')+2
            buffer = ''
            char = l[idx]
            x = 1
            while char != '=':
                buffer += char
                char = l[idx+x]
                x += 1
            code = int(buffer)
            l = l.replace(f'=={code}==',f'{line-code-1}')
        finalcode += l+'\n'
        line += 1
finalcode += f'&0 = &0'

# Finally save the code
with open('code.o','w') as file:
    file.write(finalcode)