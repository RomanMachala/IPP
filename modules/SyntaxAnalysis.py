"""
            Analyzator kodu v IPPcode24 (modul implementujici syntaktickou analyzu)

@file       modules/parse.py       
@author     Machala Roman (xmacha86)
@brief      Syntakticka analyza se stara o syntaktickou kontrolu vstupniho programu napsaneho v jazyce IPPcode24. Spojuje vsechny moduly dohromady
            a zajistuje jejich spravny chod.
"""

from .CodeGen import CodeGen
from .LexicalAnalysis import Token, TokenList, TokenType
from .definitions import *


"""
    Syntakticka analyza dostane list tokenu od lexikalni analyzy. Prochazi jej a kontroluje syntaktickou spravnost programu.
    Pro jednotlive instrukce jsou implementovane samomstatne metody, ktere zajistuji syntaktickou spravnost dane instrukce.
    Zaroven zajistuje informace pro STATP rozsireni pro tridu Statistics.

"""
class SyntaxAnalysis:
    def __init__(self, token_list: TokenList):
        self.TokenList = token_list #list tokenu, jiz se jedna o objekt s implementovanymi metodami
        self.return_code = 0 #implicitne nastaveny return code na 0)
        self.code = CodeGen()
        self.opcodes = list() #seznam vsech pouzitych istrukci
        self.labels_all = list()
        self.jumps_backward = 0
        self.jumps_not_defined = list()
        self.loc = 0
    
    #pomocna metoda pro nalezeni header .IPPcode24      
    def comment_header(self):
        self.TokenList.next_token()
        if self.TokenList.is_active():
            match self.TokenList.active_token.TokenType:
                case TokenType.EOL:
                    self.TokenList.next_token()
                    self.parse_header()
                case TokenType.EOF:
                    raise EXC_HEADER
                case _:
                    self.comment_header()
        else:
            raise EXC_INTERNAL
    
    #metoda zpracovavajici hlavicku programu
    def parse_header(self):
        #pred hlavickou mohou byt prazdne radky, komentare
        if self.TokenList.is_active():
            match self.TokenList.active_token.TokenType:
                case TokenType.KW_HEADER:
                    self.new_line()
                case TokenType.EOF:
                    raise EXC_HEADER  #pokud nalezneme konec souboru bez hlavicky, koncime s chybou
                case TokenType.EOL:
                    self.TokenList.next_token()
                    self.parse_header()
                case TokenType.COMMENT: 
                    self.comment_header()
                case _:
                    raise EXC_HEADER
        else:
            raise EXC_INTERNAL
        
    #hlavni telo parseru
    def parse(self):
        self.TokenList.next_token() #ziskame nasledujici token
        if self.TokenList.is_active():
            if self.TokenList.active_token.TokenType not in [TokenType.EOL, TokenType.EOF]:
                self.opcodes.append(self.TokenList.active_token.TokenType) #prida instrukci do seznamu
            if self.TokenList.active_token.TokenType not in [TokenType.EOL, TokenType.EOF, TokenType.COMMENT]:
                self.loc += 1
                self.code.add_instruction(self.TokenList.active_token.lexem)
            match self.TokenList.active_token.TokenType:
                case TokenType.EOL:
                    self.parse() #preskakujeme prazdne radky
                case TokenType.COMMENT:
                    self.comment()
                    #print('Koment prosel')
                case TokenType.EOF:
                    #print('Uspesna syntakticka analyza')
                    pass
                case TokenType.KW_MOVE:
                    self.inst_move(0)
                    #print('MOVE prosel')
                case TokenType.KW_CFRAME: 
                    self.new_line() #u instrukce CREATEFRAME neni treba nic kontrolovat
                    #print('CREATEFRAME prosel')
                case TokenType.KW_PUFRAME:
                    self.new_line()
                    #print('PUSHFRAME prosel')
                case TokenType.KW_POFRAME:
                    #print('POPFRAME prosel')
                    self.new_line()
                case TokenType.KW_DEF:
                    self.defvar()
                    #print('DEFVAR prosel')
                case TokenType.KW_CALL:
                    self.call()
                    #print('CALL prosel')
                case TokenType.KW_RETURN:
                    self.new_line()
                    #print('RETURN prosel')
                case TokenType.KW_PUSHS:
                    self.pushs()
                    #print('PUSHS prosel')
                case TokenType.KW_POPS:
                    self.pops()
                    #print('POPS prosel')
                case TokenType.KW_ADD | TokenType.KW_SUB | TokenType.KW_MUL | TokenType.KW_DIV:
                    self.arit_oper(0)
                    #print('ARIT_OPER prosel')
                case TokenType.KW_LT | TokenType.KW_GT | TokenType.KW_EQ:
                    self.rel_oper(0)
                    #print('REL_OPER prosel')
                case TokenType.KW_AND | TokenType.KW_OR:
                    self.and_or_oper(0)
                    #print('AND_OR prosel')
                case TokenType.KW_NOT:
                    self.not_oper(0)
                    #print('NOT prosel')
                case TokenType.KW_STRI2INT:
                    self.stri2int(0)
                    #print('STRI2INT prosel')
                case TokenType.KW_INT2CHAR:
                    self.int2char(0)
                    #print('INT2CHAR prosel')
                case TokenType.KW_READ:
                    self.read(0)
                    #print('READ prosel')
                case TokenType.KW_WRITE:
                    self.write()
                    #print('WRITE prosel')
                case TokenType.KW_CONCAT:
                    self.concat(0)
                    #print('CONCAT prosel')
                case TokenType.KW_STRLEN:
                    self.strlen(0)
                    #print('STRLEN prosel')
                case TokenType.KW_GETCHAR:
                    self.getchar(0)
                    #print('GETCHAR prosel')
                case TokenType.KW_SETCHAR:
                    self.setchar(0)
                    #print('SETCHAR prosel')
                case TokenType.KW_TYPE:
                    self.type(0)
                    #print('TYPE prosel')
                case TokenType.KW_LABEL:
                    self.label()
                    #print('LABEL prosel')
                case TokenType.KW_JUMP:
                    self.jump()
                    #print('JUMP prosel')
                case TokenType.KW_JUMPIFEQ | TokenType.KW_JUMPIFNEQ:
                    self.cond_jump(0)
                    #print('COND_JUMP prosel')
                case TokenType.KW_EXIT:
                    self.exit_oper()
                    #print('EXIT prosel')
                case TokenType.KW_DPRINT:
                    self.dprint()
                    #print('DPRINT prosel')
                case TokenType.KW_BREAK:
                    self.new_line()
                    #print('BREAK prosel')
                case _:
                    raise EXC_OPERAND
        else:
            raise EXC_INTERNAL #nemuze nastat, pro jistotu (list by nemel byt prazdny ani neaktivni)
    
    def inst_move(self, which_run: int):
        #DEFVAR <var> <sym/var>
        self.TokenList.next_token() #ziskame dalsi token
        if self.TokenList.is_active(): #pokud je aktivni list
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.inst_move(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.INT_CONST, TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    def defvar(self):
        #DEFVAR <var>
        self.TokenList.next_token() #ziskame dalsi token
        if self.TokenList.is_active():
            if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                self.code.add_var_const(self.TokenList.active_token)
                self.new_line()
            else:
                raise EXC_OTHER #pokud nenasleduje <var>
        else:
            raise EXC_INTERNAL

    def call(self):
        #CALL <label>
        self.TokenList.next_token() #ziskame dalsi token
        if self.TokenList.is_active():
            if self.TokenList.active_token.TokenType not in [TokenType.COMMENT, TokenType.TEXT, TokenType.KW_HEADER, TokenType.UNDEFINED, TokenType.EOL, TokenType.EOF, TokenType.INT_CONST, TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.IDENTIFIKATOR]:
                self.code.add_label(self.TokenList.active_token)
                self.new_line()
            else:
                raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    def pushs(self):
        #PUSHS <symb>
        self.TokenList.next_token() #ziskame dalsi token
        if self.TokenList.is_active():
            if self.TokenList.active_token.TokenType in [TokenType.IDENTIFIKATOR, TokenType.INT_CONST, TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST]:
                self.code.add_var_const(self.TokenList.active_token)
                self.new_line()
            else:
                raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    def pops(self):
        #POPS <var>
        self.TokenList.next_token() #ziskame dalsi token
        if self.TokenList.is_active():
            if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                self.code.add_var_const(self.TokenList.active_token)
                self.new_line()
            else:
                raise EXC_OTHER
        else:
            raise EXC_INTERNAL

    def arit_oper(self, which_run: int):
        #{ADD, SUB, MUL, IDIV} <var> <symb1> <symb2> (operandy musi byt typu int)
        self.TokenList.next_token() #ziskame dalsi token
        if self.TokenList.is_active():
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.arit_oper(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.arit_oper(2)
                    else:
                        raise EXC_OTHER
                case 2:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL
           
    def rel_oper(self, which_run: int):
        #{LT, GT, EQ} <var> <symb1> <symb2>
        self.TokenList.next_token() #ziskame dalsi token
        if self.TokenList.is_active():
            match which_run: #reprezentuje, ktery operand aktualne zpracovavame
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.rel_oper(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.rel_oper(2)
                    else:
                        raise EXC_OTHER
                case 2:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    def and_or_oper(self, which_run: int):
        #{AND, OR} <var> <symb1> <symb2>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.and_or_oper(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.and_or_oper(2)
                    else:
                        raise EXC_OTHER
                case 2:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL
   
    def not_oper(self, which_run: int):
        #NOT <var> <symb>
        self.TokenList.next_token()#ziskame dalsi token
        if self.TokenList.is_active():
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.not_oper(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    def stri2int(self, which_run: int):
        #STRI2INT <var> <symb1> <symb2>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.stri2int(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.stri2int(2)
                    else:
                        raise EXC_OTHER
                case 2:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    def int2char(self, which_run: int):
        #INT2CHAR <var> <symb>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.int2char(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    def read(self, which_run: int):
        #READ <var> <type>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.read(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType == TokenType.TYPE:
                        self.code.add_type(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER      
        else:
            raise EXC_INTERNAL
    
    def write(self):
        #WRITE <symb>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            if self.TokenList.active_token.TokenType in [TokenType.INT_CONST, TokenType.STR_CONST, TokenType.NIL_CONST, TokenType.BOOL_CONST, TokenType.IDENTIFIKATOR]:
                self.code.add_var_const(self.TokenList.active_token)
                self.new_line()
            else:
                raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    def concat(self, which_run: int):
        #CONCAT <var> <symb1> <symb2>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.concat(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.concat(2)
                    else:
                        raise EXC_OTHER
                case 2:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL

    def strlen(self, which_run: int):
        #STRLEN <var> <symb>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.strlen(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    def getchar(self, which_run: int):
        #GETCHAR <var> <symb1> <symb2>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.getchar(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.getchar(2)
                    else:
                        raise EXC_OTHER
                case 2:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    def setchar(self, which_run: int):
        #SETCHAR <var> <symb1> <symb2>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.setchar(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.setchar(2)
                    else:
                        raise EXC_OTHER
                case 2:
                    if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL
        
    
    def type(self, which_run: int):
        #TYPE <var> <symb>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType == TokenType.IDENTIFIKATOR:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.type(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.IDENTIFIKATOR, TokenType.INT_CONST, TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    def label(self):
        #LABEL <label>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            if self.TokenList.active_token.TokenType not in [TokenType.COMMENT, TokenType.TEXT, TokenType.KW_HEADER, TokenType.UNDEFINED, TokenType.EOL, TokenType.EOF, TokenType.INT_CONST, TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.IDENTIFIKATOR]:
                self.code.add_label(self.TokenList.active_token)
                self.add_label(self.TokenList.active_token.lexem)
                self.new_line()
            else:
                raise EXC_OTHER
        else:
            raise EXC_INTERNAL
            
    def jump(self):
        #JUMP <label>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            if self.TokenList.active_token.TokenType not in [TokenType.COMMENT, TokenType.TEXT, TokenType.KW_HEADER, TokenType.UNDEFINED, TokenType.EOL, TokenType.EOF, TokenType.INT_CONST, TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.IDENTIFIKATOR]:
                self.code.add_label(self.TokenList.active_token)
                self.check_jump(self.TokenList.active_token.lexem)
                self.new_line()
            else:
                raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    def cond_jump(self, which_run: int):
        #{JUMPIFEQ, JUMPIFNEQ} <label> <symb1> <symb2>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            match which_run:
                case 0:
                    if self.TokenList.active_token.TokenType not in [TokenType.COMMENT, TokenType.TEXT, TokenType.KW_HEADER, TokenType.UNDEFINED, TokenType.EOL, TokenType.EOF, TokenType.INT_CONST, TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.IDENTIFIKATOR]:
                        self.code.add_label(self.TokenList.active_token)
                        self.check_jump(self.TokenList.active_token.lexem)
                        self.cond_jump(1)
                    else:
                        raise EXC_OTHER
                case 1:
                    if self.TokenList.active_token.TokenType in [TokenType.IDENTIFIKATOR, TokenType.INT_CONST, TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.cond_jump(2)
                    else:
                        raise EXC_OTHER
                case 2:
                    if self.TokenList.active_token.TokenType in [TokenType.IDENTIFIKATOR, TokenType.INT_CONST, TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST]:
                        self.code.add_var_const(self.TokenList.active_token)
                        self.new_line()
                    else:
                        raise EXC_OTHER
        else:
            raise EXC_INTERNAL

    def exit_oper(self):
        #EXIT <symb>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            if self.TokenList.active_token.TokenType in [TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST, TokenType.INT_CONST, TokenType.IDENTIFIKATOR]:
                self.code.add_var_const(self.TokenList.active_token)
                self.new_line()
            else:
                raise EXC_OTHER
        else:
            raise EXC_INTERNAL 
    
    def dprint(self):
        #DPRINT <symb>
        self.TokenList.next_token()
        if self.TokenList.is_active():
            if self.TokenList.active_token.TokenType in [TokenType.IDENTIFIKATOR, TokenType.INT_CONST, TokenType.STR_CONST, TokenType.BOOL_CONST, TokenType.NIL_CONST]:
                self.code.add_var_const(self.TokenList.active_token)
                self.new_line()
            else:
                raise EXC_OTHER
        else:
            raise EXC_INTERNAL
    
    #metoda zpracovavajici komentare
    def comment(self):
        self.TokenList.next_token()
        if self.TokenList.is_active():
            if self.TokenList.active_token.TokenType == TokenType.EOL:
                self.parse()
            elif self.TokenList.active_token.TokenType == TokenType.EOF:
                new_token = Token(TokenType.EOF, '')
                self.TokenList.token_list.append(new_token)
                self.parse()
            else:
                self.comment()
        else:
            raise EXC_INTERNAL
        
    #meotoda zajistujici ukonceni radku, je volana pokazdne, kdyz je ocekavan novy radek, umoznuje kontrolu ze kazda instrukce je na 1 radku 
    def new_line(self):
        self.TokenList.next_token()
        if self.TokenList.is_active():
            match self.TokenList.active_token.TokenType:
                case TokenType.EOL:
                    self.parse()
                case TokenType.EOF:
                    new_token = Token(TokenType.EOF, '')
                    self.TokenList.token_list.append(new_token)
                    self.parse()
                case TokenType.COMMENT:
                    self.comment()
                case _:
                    raise OtherError
        else:
            raise EXC_INTERNAL
    
    #metoda pridavajici navesti do seznamu - pro STATP rozsireni
    def add_label(self, label: str):
        self.labels_all.append(label) #prida label do seznamu labelu
        pass

    #podpurna metoda pro STATP rozsireni, rozhoduje zda se jedna o skok dozadu nebo jeste neni rozhodnuto
    def check_jump(self, label: str):
        if label in self.labels_all:
            self.jumps_backward += 1 #pokud skaceme na label, ktera je v seznamu, jedna se o skok zpet
        else:
            self.jumps_not_defined.append(label) #pridame label, ktera jeste nebyla definovana