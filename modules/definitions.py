"""
            Analyzator kodu v IPPcode24 (Podpurnny modul pro definice)

@file       modules/definitions.py       
@author     Machala Roman (xmacha86)
@brief      Definice jednotlivych podpurnych trid, regularnich vyrazu, navratovych kodu atd. Hlavnim ucelem je udrzet citelnsot kodu
"""

CORRECT = 0 #bez problemu
PARAM_ERROR = 10 #chyba zpusobena chybnym parametrem (chybejici, zakazana kombinace)
DUPLICITE_FILES = 12 #duplicitni soubory pri STATP rozsireni
INTERNAL_ERROR = 99 #interni chyby (zpusobene behem programu)

MISSING_HEADER = 21
ERROR_OPERAND = 22
OTHER_ERROR = 23

#jednotlive vyjimky
class InternalError(Exception):
    pass

class MissingHeaderError(Exception):
    pass

class ErrorOperand(Exception):
    pass

class OtherError(Exception):
    pass

EXC_INTERNAL = InternalError("Internal error occurred")
EXC_HEADER = MissingHeaderError("Missing or incorrect header")
EXC_OPERAND = ErrorOperand("Invalid operand error")
EXC_OTHER = OtherError("Other error")

#reprezentace jednotlivych prepinacu pro paramentr --stats
#umoznuje lehci manipulaci, ktere statistiky nasledne vytisknout
class StatType:
    LOC = "LOC"
    COMMENTS = "COMMENTS"
    LABELS = "LABELS"
    JUMPS = "JUMPS"
    FWJUMPS = "FWJUMPS"
    BACKJUMPS = "BACKJUMPS"
    BADJUMPS = "BADJUMPS"
    FREQUENT = "FREQUENT"
    EOL = "EOL"

#vytiskne pomoc pri parametru --help
def help():
    print("""
          Script typu filtr. Nacita ze STDIN program sepsany v jazyce IPPcode24,
          kontroluje jeho lexikalni a syntaktickou spravnost a generuje
          na STDOUT XML reprezentaci.
          
          usage: python3.10 parse.py [--help] [--stats=file [SWITCHES]]
            --help          : vytiskne tuto pomoc
            --stats=file    : umoznuje sbirat ruzne statistiky do souboru file
            
            SWITHCES
            --loc           : pocita pocet radku kodu
            --labels        : pocita pocet navesti
            --jumps         : pocita pocet skoku
            --fwjumps       : pocita pocet doprednych skoku
            --backjumps     : pocita pocet zpetnych skoku
            --badjumps      : pocita pocet spatnych skoku
            --frequent      : pocita nejcasteji vyskytujici se instrukce
            --eol           : prida do vystupniho souboru zalomeni radku
            --comments      : pocita pocet komentaru
            --print=string  : umoznuje vytisnout retezec string do souboru 
          """)

#trida typ tokenu
class TokenType:
    KW_HEADER = 'KW_HEADER'
    KW_WHITESPACE ='KW_WHITESPACE'
    KW_CFRAME = 'KW_CFRAME'
    KW_PUFRAME = 'KW_PUFRAME'
    KW_POFRAME = 'KW_POFRAME'
    KW_MOVE = 'KW_MOVE'
    KW_DEF = 'KW_DEF'
    KW_CALL = 'KW_CALL'
    KW_RETURN = 'KW_RETURN'
    KW_PUSHS = 'KW_PUSHS'
    KW_POPS = 'KW_POPS'
    KW_ADD = 'KW_ADD'
    KW_SUB = 'KW_SUB'
    KW_MUL = 'KW_MUL'
    KW_DIV = 'KW_DIV'
    KW_LT = 'KW_LT'
    KW_GT = 'KW_GT'
    KW_EQ = 'KW_EQ'
    KW_AND = 'KW_AND'
    KW_OR = 'KW_OR'
    KW_NOT = 'KW_NOT'
    KW_INT2CHAR = 'KW_INT2CHAR'
    KW_STRI2INT = 'KW_STRI2INT'
    KW_READ = 'KW_READ'
    KW_WRITE = 'KW_WRITE'
    KW_CONCAT = 'KW_CONCAT'
    KW_STRLEN = 'KW_STRLEN'
    KW_GETCHAR = 'KW_GETCHAR'
    KW_SETCHAR = 'KW_SETCHAR'
    KW_TYPE = 'KW_TYPE'
    KW_JUMP = 'KW_JUMP'
    KW_AND = 'KW_AND'
    KW_JUMPIFEQ = 'KW_JUMPIFEQ'
    KW_JUMPIFNEQ = 'KW_JUMPIFNEQ'
    KW_EXIT = 'KW_EXIT'
    COMMENT = 'COMMENT'
    KW_LABEL = 'KW_LABEL'
    BOOL_CONST = 'BOOL_CONST'
    INT_CONST = 'INT_CONST'
    STR_CONST = 'STR_CONST'
    NIL_CONST = 'NIL_CONST'
    KW_DPRINT = 'KW_DRPINT'
    KW_BREAK = 'KW_BREAK'
    
    LABEL = 'LABEL'
    TEXT = 'TEXT'
    #IDENTIFIER = 'IDENTIFIER'
    TYPE = 'TYPE'
    
    IDENTIFIKATOR = 'IDENTIFIKATOR'
    UNDEFINED = 'UNDEFINED'
    #WHITESPACE = 'WHITESPACE'
    EOL = 'EOL'
    EOF = 'EOF'
    
#definice regularnich vyrazu pro jednotlive klicove slova, identifikatory atd.
keyword_patterns = {
    'KW_HEADER'         : r'(?i)\.ippcode24$',
    #'WHITESPACE'       : r' ',
    'EOL'               : r'\n',
    #'CONST'            : r'[0-9]+|\-[0-9]+|nil|true|false',
    'KW_CFRAME'         : r'(?i)createframe$',
    'KW_PUFRAME'        : r'(?i)pushframe$',
    'KW_POFRAME'        : r'(?i)popframe$',
    'KW_MOVE'           : r'(?i)move$',
    'KW_DEF'            : r'(?i)defvar$', 
    'KW_CALL'           : r'(?i)call$',
    'KW_RETURN'         : r'(?i)return$',
    'KW_PUSHS'          : r'(?i)pushs$',
    'KW_POPS'           : r'(?i)pops$',
    'KW_ADD'            : r'(?i)add$',
    'KW_SUB'            : r'(?i)sub$',
    'KW_MUL'            : r'(?i)mul$',
    'KW_DIV'            : r'(?i)idiv$',
    'KW_LT'             : r'(?i)lt$',
    'KW_GT'             : r'(?i)gt$',
    'KW_EQ'             : r'(?i)eq$',
    'KW_AND'            : r'(?i)and$',
    'KW_OR'             : r'(?i)or$',
    'KW_NOT'            : r'(?i)not$',
    'KW_INT2CHAR'       : r'(?i)int2char$',
    'KW_STRI2INT'       : r'(?i)stri2int$',
    'KW_READ'           : r'(?i)read$',
    'KW_WRITE'          : r'(?i)write$',
    'KW_CONCAT'         : r'(?i)concat$',
    'KW_STRLEN'         : r'(?i)strlen$',
    'KW_GETCHAR'        : r'(?i)getchar$',
    'KW_SETCHAR'        : r'(?i)setchar$',
    'KW_TYPE'           : r'(?i)type$',
    'KW_JUMP'           : r'(?i)jump$',
    'KW_AND'            : r'(?i)and$',
    'KW_JUMPIFEQ'       : r'(?i)jumpifeq$',
    'KW_JUMPIFNEQ'      : r'(?i)jumpifneq$',
    'KW_EXIT'           : r'(?i)exit$',
    'COMMENT'           : r'#.*$',
    #'KW_GF'            : r'GF',
    #'KW_LF'            : r'LF',
    #'KW_TF'            : r'TF',
    'KW_LABEL'          : r'(?i)label$',
    'KW_DRPINT'         : r'(?i)dprint$',
    'KW_BREAK'          : r'(?i)break$',
    #'KW_INT'           : r'int',
    #'KW_STRING'        : r'string',
    #'KW_BOOL'          : r'bool',
    #'KW_TRUE'          : r'true',
    #'KW_FALSE'         : r'false',
    #'IDENTIFIER'       : r'[a-zA-Z_\-&%*!?$][a-zA-Z0-9_\-&%*!?$]*',    
    'INT_CONST'         : r'int@(\-?|\+?)(0[xX][0-9a-fA-F]+|0[oO][0-7]+|[0-9]+)$',
    'STR_CONST'         : r'string@(?:\\[0-9]{3}|[^\s\\])*$',
    'BOOL_CONST'        : r'bool@true$|bool@false$',
    'NIL_CONST'         : r'nil@nil$',
    'IDENTIFIKATOR'     : r'(GF|LF|TF)@[a-zA-Z_\-&%*!?$][a-zA-Z0-9_\-&%*!?$]*$',
    'TYPE'              : r'int$|string$|bool$',
    
    'LABEL'             : r'^[^@/\\][a-zA-Z_\-&%*!?$]{0,1}[a-zA-Z0-9_\-&%*!?$]+$', #odpovida identifikatorum
    'TEXT'              : r'^(?:\\[0-9]{3}|[^\s\\@])+$' #v podstate vse + \xyz .... x,y,z = {0-9}
    #text je univerzalni regularni vyraz spojujici identifikatory, stringy, komentare atd.,
    #az v pri syntakticke analyze se rozhodne, zdali text ma byt stringem nebo identifikatorem
    }