from ArvoreSintatica import  Node
"""
Explanation for this comment is on file 'analizadorLexico.py'

SENTENCES:

S = [Expressao]+
Expressao = (declaracao | operacao | forloop | print | ifbloco ) fimDeExpressao
declaracao = (declaradorVariavel|null) variavel (operadorDeclaracao (valor | variavel | operacao) | null)
null = 
operacao = operacaoBinaria | operacaoUnaria
operacaoBinaria = (variavel | operacao | valor) operador (variavel | operacao | valor)
operacaoUnaria = (variavel) operador operador
forloop = inicializadorFor AbreParenteses (declaracao | null) ; (condicao) ; (declaracao | null) FechaParenteses Bloco
Bloco = aberturaBloco [Expressao]+ fechamentoBloco
ifbloco = inicializadorIf AbreParenteses condicao FechaParenteses Bloco
condicao = (variavel | operacao | valor) operadorBooleano (variavel | operacao | valor)
valor = valorNumerico | valorString | valorBooleano


TOKENS:

aberturaBloco = '{'
fechamentoBloco = '}'
operadorBooleano = == | != | > | < | >= | <= | <||> | &&
operadorDeclaracao = <=>
operador = + | - | / | *
declaradorVariavel = var
inicializadorFor = for
inicializadorIf = if
fimDeExpressao = ;
variavel = [a-zA-Z]+
valorNumerico = [0-9]+
valorString = '.'
valorBooleano = true | false
AbreParenteses = (
FechaParenteses = )
"""

"""
This is a top-down parser that detects if the token list has a valid syntax and generates the syntatic tree
"""

# Simbol Table to keep track of variables
symbol_table = {
    'variables':[],
    'temporary':[]
}

# This parser receives a list of tokens

## Functions for retrieving tokens, these are all wrappers for the function get_token

def get_variable(s, declaration=False):
    variavel = get_token(s, "variavel")
    if variavel and not variavel in symbol_table['variables']:
        if not declaration:
            raise Exception(f"Variable {variavel} referenced before assigment")
        symbol_table['variables'].append(variavel)
    return variavel

def get_value(s):
    value = get_numerical_value(s)
    if not value:
        value = get_string_value(s)
        return value, 'valorString'
    return value, 'valorNumerico'

def get_value_or_var(s):
    value, tipo = get_value(s)
    if not value:
        value = get_variable(s)
        return value, "variavel"
    return value, tipo

def get_numerical_value(s):
    return get_token(s,'valorNumerico')

def get_string_value(s):
    return get_token(s,'valorString')

# This function attempts to retrieve a token of a specific type,
# or false if the token is not of that type (or doesn't exist)
def get_token(string, type):
    if len(string) <= 0:
        return False
    return string[0][1] if string[0][0] == type else False

## Functions for each tipe of non terminal expressions

# Each possible sentence described on the first comment has it's own function to validate it
# They are pretty much straight forward

# Each function returns 3 items: status, string, syntactic tree.
# status is a boolean value if the validation succeded
# string is the token list without the tokens "consumed" by the validation
# the tree is saved for later converting the code into 3AC

def ifstatement(string):
    s = string

    opif = Node('ifbloco','')

    inicializador = get_token(s,'inicializadorIf')
    s = s[1:]
    abreParen = get_token(s,'AbreParenteses')
    s = s[1:]

    dec1, s, dec1tree = conditional(s)
    opif.add_child(dec1tree)

    fechaParen = get_token(s,"FechaParenteses")
    s = s[1:]

    block, s, treeBlock = codeblock(s)
    opif.add_child(treeBlock)


    return (True,s,opif) if inicializador and abreParen and dec1 and block and fechaParen else (False,string,None)

def codeblock(string):
    s = string

    block = Node('Bloco','')

    abertura = get_token(s,'aberturaBloco')
    if not abertura:
        return False, string, None
    s = s[1:]
    next_token = get_token(s,'fechamentoBloco')
    while not next_token and len(s) > 0:
        result, s, exp = expressao(s)
        block.add_child(exp)
        if not result:
            return False, string, None
        next_token = get_token(s,'fechamentoBloco')
    if len(s) <= 0:
        return False, string, None
    return True, s[1:], block

def conditional(string):
    s = string

    opcon = Node('condicao','')


    value1, s, var1 = operacao(s)
    var1type = "operacao"
    if not value1:
        value1, var1type = get_value_or_var(s) 
        s = s[1:]
        var1 = Node(var1type,value1)

    if var1type == 'valorString':
        return False, string, None

    operador = get_token(s,"operadorBooleano")
    op1 = Node('operadorBooleano',operador)
    opcon.add_child(op1)
    s = s[1:]

    value2, s, var2 = operacao(s)
    var2type = "operacao"
    if not value2:
        value2, var2type = get_value_or_var(s)
        s = s[1:]
        var2 = Node(var2type,value2)

    if var2type == 'valorString':
        return False, string, None

    op1.add_child(var1)
    op1.add_child(var2)

    return (True, s, opcon) if value2 and value1 and operador else (False, string, None)

def forloop(string):
    s = string

    opfor = Node('forloop','')

    inicializador = get_token(s,'inicializadorFor')
    if not inicializador:
        return False, None, string
    s = s[1:]
    abreParen = get_token(s,'AbreParenteses')
    s = s[1:]

    dec1, s, dec1tree = declaracao(s)
    if dec1:
        dec1node = Node('inicializador','',[dec1tree])
        opfor.add_child(dec1node)

    fimexp1 = get_token(s,"fimDeExpressao")
    s = s[1:]

    dec2, s, dec2tree = conditional(s)
    opfor.add_child(dec2tree)

    fimexp2 = get_token(s,"fimDeExpressao")
    s = s[1:]

    dec3, s, dec3tree = operacao(s)
    if not dec3:
        dec3, s, dec3tree = declaracao(s)
    if dec3:
        dec3node = Node('finalizador','',[dec3tree])
        opfor.add_child(dec3node)

    fechaParen = get_token(s,"FechaParenteses")
    s = s[1:]

    block, s, treeBlock = codeblock(s)
    opfor.add_child(treeBlock)

    return (True, s, opfor) if inicializador and abreParen and dec2 and fechaParen and block else (False, string, None)

def declaracao(string):
    if len(string) <= 0:
        return False, string, None
    dec = Node('declaration','')
    s = string

    declarador = get_token(s,"declaradorVariavel")
    if not declarador:
        if s[0][0] != "variavel":
            return False,string, None
        dec.type = "assigment"
    else:
        s = s[1:]

    variavel = get_variable(s,dec.type == "declaration")
    if not variavel:
        return False,string, None
    dec.value = variavel

    if not variavel in symbol_table['variables']:
        if not dec.type == "declaration":
            raise Exception(f"Variable {variavel} referenced before assigment")
        symbol_table['variables'].append(variavel)
    s = s[1:]

    operador = get_token(s,"operadorDeclaracao")
    if not operador:
        return True, s, dec
    s = s[1:]

    op, s, optree = operacao(s)
    if op:
        dec.add_child(optree)
        return True,s,dec


    valor, valorType = get_value_or_var(s)
    if valor:
        dec.add_child(Node(valorType,valor))
        return True,s[1:],dec
    return False,string,None
    
def operacao(string):
    if len(string) < 3:
        return False, string, None
    result, s, op = operacaoUnaria(string)
    if result:
        return True, s, op

    # Operations are built from the left to right
    # A+B+C+D+E if built as
    # (((A+B)+C)+D)+E
    result, s, base_op = operacaoBinaria(string)
    if not result:
        return False, string, None
    while result:
        # Attempt to build operations until they are not valid
        result, s, op = operacaoBinariaIncompleta(s)
        if op:
            op.add_child(base_op)
            base_op = op

    ## This will apply a tree root inversion to fix operation order
    base_op = resolve_multiplicative_operations(base_op)

    return True, s, base_op

# Operations more close to the leaf are done before operations closer to the root  of the syntactic tree
# This Algorithm makes sure that multiplication and division are closer to the leafs
# than addition and subtraction
def resolve_multiplicative_operations(base_op, parent = None):
    for idx, p in enumerate(base_op.children):
        if p.type != "operacao":
            continue
        temp = resolve_multiplicative_operations(p)
        base_op.children[idx] = temp

    if base_op.value == '/' or base_op.value == '*':
        for p in base_op.children:
            if p.type == "operacao" and p.value != '/' and p.value != '*':
                temp = base_op
                base_op.children.remove(p)
                base_op = p
                
                last_child = base_op.children[-1]
                if last_child.type == 'operacao':
                    last_child = base_op.children[-2]
                base_op.children.remove(last_child)
                temp.add_child(last_child)

                temp2 = resolve_multiplicative_operations(temp)
                base_op.add_child(temp2)
                
                break
    return base_op

def operacaoBinaria(string):
    s = string

    value1, var1type = get_value_or_var(s)
    var1 = Node(var1type,value1)
    if var1type == 'valorString':
        return False, string, None

    operador = get_token(s[1:],"operador")
    value2, var2type = get_value_or_var(s[2:])
    var2 = Node(var2type,value2)
    if var2type == 'valorString':
        return False, string, None

    op = Node('operacao',operador)
    op.add_child(var1)
    op.add_child(var2)
    
    return (True, string[3:], op) if value1 and value2 and operador else (False, string, None)

def operacaoBinariaIncompleta(string):
    if len(string) < 2:
        return False, string, None
    s = string

    value, vartype = get_value_or_var(s[1:])
    var = Node(vartype,value)
    if vartype == 'valorString':
        return False, string, None

    operador = get_token(s,"operador")
    op = Node('operacao',operador)
    op.add_child(var)
    return (True, string[2:], op) if value and operador else (False, string, None)

def operacaoUnaria(string):
    value, vartype = get_value_or_var(string)
    var = Node(vartype,value)
    if vartype == 'valorString':
        return False, string, None
    operador1 = get_token(string[1:],"operador") if get_token(string[1:],"operador") in ['+','-'] else False
    operador2 = get_token(string[2:],"operador") if get_token(string[2:],"operador") == operador1 else False

    # X++ is the same as
    # X = X + 1
    # This node converts it to a full binary operation
    dec = Node('operacao','unary')
    op = Node('operacao',operador1)
    increment = Node('valorNumerico',1)

    op.add_child(var)
    op.add_child(increment)

    dec.add_child(op)
    
    return (True,string[3:],dec) if value and operador1 and operador2 else (False,string,None)

# This node will attempt to match an expression to any possible sentence
def expressao(string):
    exp = Node('expression','')

    result, s, dec = declaracao(string)
    if result:
        if s[0][0] == "fimDeExpressao":
            exp.add_child(dec)
            return True, s[1:], exp

    result, s, op = operacao(string)
    if result:
        if s[0][0] == "fimDeExpressao":
            exp.add_child(op)
            return True, s[1:], exp

    result, s, fl = forloop(string)
    if result:
        if s[0][0] == "fimDeExpressao":
            exp.add_child(fl)
            return True, s[1:], exp

    result, s, ct = conditional(string)
    if result:
        if s[0][0] == "fimDeExpressao":
            exp.add_child(ct)
            return True, s[1:], exp

    result, s, it = ifstatement(string)
    if result:
        if s[0][0] == "fimDeExpressao":
            exp.add_child(it)
            return True, s[1:], exp

    return False, string, None

def S(string):
    root = Node('root','')
    s = string
    while len(s) > 0:
        result, s, exp = expressao(s)
        root.add_child(exp)
        if not result:
            return False
    return root.export()

tokens = []
with open('code.t','r') as file:
    for p in file.readlines():
        values = p.replace('\n','').split('<>')
        tokens.append((values[0],values[1]))

import json
with open('arvore.json','w') as file:
    file.write(json.dumps(S(tokens)))
with open('symbol_table.json','w') as file:
    file.write(json.dumps(symbol_table))