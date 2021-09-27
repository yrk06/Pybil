"""
This is the Language gramatic. The first block determine how sentences are built.
The second block determines what each token on a sentece is.

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
operadorBooleano = == | != | > | < | >= | <= | || | &&
operadorDeclaracao = =
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
This code is responsible to convert written code to a list of Tokens
"""
# (token_name, token_value)
tokens = []

# The following lists contain characters that end other tokens:
# For example '10>5', the character '>' marks the end of the '10' token
# while still being a token itself
# Another example '10 > 5' the empty space ' ' marks the end of the '10' token
# though this time the empty space is not a valid token
endskipchars = [' ','\n']
endnotskipchars = [';','(',')','','+','-','/','*','}','=','!','>','<','|','&',]

# Text is the string that will be parsed into tokens
text = ""
with open('code.y', 'r') as file:
    text = file.read()

# Buffer is a string of charactes.
# Since some tokens are multiple characters in length it's necessary
# to store them while being read
buffer = ""

# This function takes the buffer after receiving a end-token-character
# and tries to match it to any of the possible existing tokens
def attempt_token(char):
    global buffer
    if buffer == '':
        return
    try:
        # Tries to convert the token into a numerical value
        value = float(buffer)
        tokens.append( ('valorNumerico',value) )
        buffer = ""
    except:
        # If the buffer starts with single quotes, treat it as a string
        if not (buffer.startswith('\'') or buffer.endswith('\'')):

            ## not numerical tokens cannot start with numbers
            if buffer[0] in list(map(lambda a: str(a),range(10))):
                raise ValueError(f'Invalid token {idx}')

            # Since both tokens = and == have the same starting value
            # and the = is a end-token-character, this makes sure
            # == is not interpreted as 2 different tokens
            if buffer == "=" and char != "=":
                tokens.append( ('operadorDeclaracao',buffer))
                buffer = ""

            # The above is also true for the tokens <= >= < and >
            elif buffer in ['>','<'] and char != '=':
                tokens.append( ('operadorBooleano',buffer))
            
            # In case the next char is a = and the buffer was any of the above
            # Continue the process (stop trying to match the current buffer to a token)
            elif (buffer == "=" or buffer in ['>','<'])  and char == "=":
                return
            else:

                # if none of the other options was correct
                # Attemp these final methods of matching the first
                # Chars as specific tokens and then re-run the Matching Algorithm
                if buffer.startswith("=="):
                    tokens.append( ('operadorBooleano',buffer[0:2]))
                    buffer = buffer[2:]
                    attempt_token(char)

                elif buffer.startswith('>') or buffer.startswith('<'):
                    tokens.append( ('operadorBooleano',buffer[0]))
                    buffer = buffer[1:]
                    attempt_token(char)

                elif buffer.startswith("="):
                    tokens.append( ('operadorDeclaracao',buffer[0]))
                    buffer = buffer[1:]
                    attempt_token(char)

                else:
                    ## If none of the above matching worked, then this token is a valid variable
                    tokens.append( ('variavel',buffer) )
                
        else:
            tokens.append( ('valorString',buffer) )
        # Empty the buffer to read another Token
        buffer = ""

# This loop will go through all characters in the code
for idx, char in enumerate(text):

    # If this character is a end-token-character call the function to match it
    if char in endskipchars or char in endnotskipchars:
        if buffer != "":
            attempt_token(char)
        if not char in endnotskipchars:
            continue

    buffer += char

    # These if-elif chains try to match the current buffer to the following tokens
    # The tokens that are missing here are attempted to be matched in the `attempt_token` function
    if buffer == "var":
        tokens.append( ('declaradorVariavel','var') )
        buffer = ""
    elif buffer == "for":
        tokens.append( ('inicializadorFor','for') )
        buffer = ""
    elif buffer == "if":
        tokens.append( ('inicializadorIf','if') )
        buffer = ""
    elif buffer == ";":
        tokens.append( ('fimDeExpressao',';') )
        buffer = ""
    elif buffer == "(":
        tokens.append( ('AbreParenteses','(') )
        buffer = ""
    elif buffer == ")":
        tokens.append( ('FechaParenteses',')') )
        buffer = ""
    elif buffer == "true":
        tokens.append( ('valorBooleano',buffer))
        buffer = ""
    elif buffer in ['==','!=','>=','<=','||','&&']:
        tokens.append( ('operadorBooleano',buffer))
        buffer = ""
    elif buffer in ['+','-','/','*']:
        tokens.append( ('operador',buffer))
        buffer = ""
    elif buffer == '{':
        tokens.append( ('aberturaBloco',buffer))
        buffer = ""
    elif buffer == '}':
        tokens.append( ('fechamentoBloco',buffer))
        buffer = ""

# One final call to match what was left in the buffer
attempt_token(' ')


# This loop will save the token list
with open('code.t','w') as file:
    for p in tokens:
        file.write(f'{p[0]}<>{p[1]}\n')
    