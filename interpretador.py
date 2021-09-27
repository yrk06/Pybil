"""

This is the syntax for the 3AC "Machine Code" run by this virtual processor

Expressao = ExpressaoOperacao | ExpressaoAssigment
ExpressaoOperacao = (variavel | registrador) igual (variavel | valor | registrador) operador (variavel | valor | registrador)
ExpressaoAssigment = (variavel | registrador) igual (variavel | valor | registrador)
ExpressaoCondicional = clausulaJump valor registrador 
variavel = $[0-2047]
registrador = &[0-9]+
valor = [0-9]+
igual = <=>
operador = +,-,/,*
clausulaJump = <jumpz> | <jumplz> | <jumpgz>
"""
import traceback

# Checks if the string starts with a variable and 
# return both the variable address and the remainder of the string
def variavel(string):
    if string[0] != '$':
        return None, string
    buffer = ""
    final_idx = len(string)
    for idx, c in enumerate(string[1:]):
        if c in list(map(lambda a: str(a),range(10))):
            buffer += c
        else:
            final_idx = idx+1
            break
    value = 0
    try:
        value = int(buffer)
    except:
        return None, string
    if value >= 2048:
        return None, string 
    return value, string[final_idx:].strip()

# Checks if the string starts with a value and 
# return both the value and the remainder of the string
def valor(string):
    buffer = ""
    final_idx = len(string)
    for idx, c in enumerate(string):
        if c in list(map(lambda a: str(a),range(10)))+['.']:
            buffer += c
        else:
            final_idx = idx
            break
    value = 0
    try:
        value = float(buffer)
    except:
        return None, string 
    return value, string[final_idx:].strip()

# Checks if the string starts with a register and 
# return both the register address and the remainder of the string
def registrador(string):
    if string[0] != '&':
        return None, string
    buffer = ""
    final_idx = len(string)
    for idx, c in enumerate(string[1:]):
        if c in list(map(lambda a: str(a),range(10))):
            buffer += c
        else:
            final_idx = idx+1
            break
    value = 0
    try:
        value = int(buffer)
    except:
        return None, string
    if value >= 5:
        return None, string 
    return value, string[final_idx:].strip()

# Checks if the string starts with an operator and 
# return both the operator and the remainder of the string
def operador(string):
    return (string[0], string[1:].strip()) if string[0] in ['+','-','/','*'] else (False, string)

# Checks if the string starts with an equal sign and 
# return both the equal sign and the remainder of the string
def igual(string):
    return (True, string[1:].strip()) if string[0] == '=' else (False, string)

# Checks if the string starts with a jump clause and 
# return both the jump clause and the remainder of the string
def clausulaJump(string):
    buffer = ""
    final_idx = len(string)
    for idx, c in enumerate(string):
        buffer += c
        if buffer == 'jmpz':
            return 'jmpz',string[idx+1:].strip()
        elif buffer == 'jmplz':
            return 'jmplz',string[idx+1:].strip()
        elif buffer == 'jmpgz':
            return 'jmpgz',string[idx+1:].strip()
    return False,string

# This function tests if a command is an operation and executes it
def expressaoOperacao(string):
    resultmemory = memory
    v1memory = memory
    v2memory = memory
    
    registerWrite = False
    result, s = variavel(string)
    if not result and result != 0:
        result, s = registrador(string)
        resultmemory = registers
        registerWrite = True
    
    equal, s = igual(s)

    v1, s = variavel(s)
    if not v1 and v1 != 0:
        v1, s = registrador(s)
        v1memory = registers 
    if not v1 and v1 != 0:
        v1, s = valor(s)
        v1memory = None

    try:
        op, s = operador(s)
    except:
        return False,string

    v2, s = variavel(s)
    if not v2 and v2 != 0:
        v2, s = registrador(s)
        v2memory = registers
    if not v2 and v2 != 0:
        v2, s = valor(s)
        v2memory = None

    if not ((result != False or result == 0) and (v1 != False or v1 == 0) and  op and (v2 != False or v2 == 0) and s == ""):
        return False, string

    value1 = v1memory[v1] if v1memory else v1
    value2 = v2memory[v2] if v2memory else v2
    resultmemory[result] = resolveOperation(value1,value2,op)

    if registerWrite:
        if result == 4:
            print(resultmemory[result])
        if result == 3:
            print(chr(resultmemory[result]),end="")
    return True, s

# This function tests if a command is an assigment and executes it
def expressaoAssigment(string):
    resultmemory = memory
    v1memory = memory
    
    registerWrite = False

    result, s = variavel(string)
    if not result and result != 0.0:
        result, s = registrador(string)
        resultmemory = registers
        registerWrite = True

    equal, s = igual(s)

    v1, s = variavel(s)
    if not v1 and v1 != 0.0:
        v1, s = registrador(s)
        v1memory = registers 
    if not v1 and v1 != 0.0:
        v1, s = valor(s)
        v1memory = None

    if not ((result != False or result == 0) and (v1 != False or v1 == 0) and s == ""):
        return False, string

    
    resultmemory[result] = v1memory[v1] if v1memory else v1
    if registerWrite:
        if result == 4:
            print(resultmemory[result])
        if result == 3:
            print(chr(resultmemory[result]),end="")
    return True, s

# This function tests if a command is a conditional jump and executes it
def expressaoCondicional(string):
    command,s = clausulaJump(string)
    v1, s = valor(s)
    rg, s = registrador(s)
    if not (command != False and (rg != False or rg == 0) and (v1 != False or v1 == 0) and s == ""):
        return False, string
    
    if command == 'jmpz':
        if registers[rg] == 0:
            registers[0] = v1 - 1
    elif command == 'jmplz':
        if registers[rg] < 0:
            registers[0] = v1 - 1
    elif command == 'jmpgz':
        if registers[rg] > 0:
            registers[0] = v1 - 1
    return True,s
    
# This tests if an expression is any valid expression and executes it
def expressao(string):
    result, s = expressaoOperacao(string)
    if not result:
        result, s = expressaoAssigment(string)
    if not result:
        result, s = expressaoCondicional(string)
    if not result:
        print(f'Error, could not identify expression at line {registers[0]+1}')

# this wrapper function resolves basic math operations
def resolveOperation(value1,value2,op):
    if op == '+':
        return value1 + value2
    elif op == '-':
        return value1 - value2
    elif op == '/':
        return value1 / value2
    elif op == '*':
        return value1 * value2

# This is the processor "Memory"
# it has 2048 slots that can hold Integer numbers or Float numbers
memory = [0] * 2048

# the registers
# 0 = Instruction counter
# 1 = No use
# 2 = No use
# 3 = Print char command
# 4 = Print number command
registers = [0] * 5

# The main program opens the code and attemps to execute it
# it stops when reaches EOF
def main():
    code = []
    with open('code.o','r') as file:
        code = file.readlines()
    while registers[0] < len(code):
        try:
            expressao(code[int(registers[0])])
        except:
            traceback.print_exc()
            print(f'at line {registers[0]}')
            break
        registers[0] += 1

main()