"""
            Analyzator kodu v IPPcode24 (Modul implementujici lexikalni analyzu)

@file       modules/LexicalAnalysis.py       
@author     Machala Roman (xmacha86)
@brief      Stara se o lexikalni spravnost vstupniho programu. Odstranuje bile znaky, komentare a generuje tokeny, ktere uklada do listu tokenu, se kterym
            nasledne pracuje syntakticka analyza.
"""

from .definitions import *
import sys
import re

"""
    Lexikalni analyza a definice tokenu a listu tokenu. Lexikalni analyza cte vstupni program a generuje jednotlive tokeny. Vysledkem je list tokenu pro syntaktickou 
    analyzu, ktera nad tinto listem pracuje.
"""
class Token:
    def __init__(self, type: str, lexem: str):
        self.TokenType = type
        self.lexem = lexem
        
    #def __eq__(self, other) -> bool: neni treba implementovat, metoda eq jiz na str existuje
       # return (self.TokenType == other.TokenType)
       
    #def __repr__(self) -> str: #pro ladici vypisy -- neni treba, pokud je primo specifikovano, ze typ a lexem jsou str
       # return f'Token {self.TokenType}, {self.lexem}'

class LexicalAnalyzer:
    def __init__(self):
        self.current_char = ''
        self.current_lexem = ''
        self.tokens = list()
        
    def get_next_char(self):
        self.current_char = sys.stdin.read(1) #nacte jeden znak z STDIN a ulozi jej jako aktualne zpracovavany
        
    def append_char_to_lexem(self, char: str):
        self.current_lexem += char #pridame nove nacteny znak do aktuale tvoreneho lexemu
    
    def match_token(self) -> TokenType:
        for type, reg_expr in keyword_patterns.items():
            if re.match(reg_expr, self.current_lexem): #pokud matchneme nejaky regex s aktualne tvorenym lexemem
                new_token = Token(type, self.current_lexem) #vytvorime novy token
                self.tokens.append(new_token) #vlozime token do seznamu tokenu
                self.current_lexem = '' #resetujeme aktualne tvoreny lexem

                return new_token.TokenType #vratime odpovidajici typ tokenu
            
        return TokenType.UNDEFINED #pokud nenajdeme token odpovidajici regularnim vyrazum, vratime nedefinovany token
    
    #hlavni metoda zpracovavajici vstupni soubor ze STDIN
    def analyze(self):
        self.get_next_char() #ziskame prvni znak
        while True:
            if not self.current_char: #konec vstupu
                if self.current_lexem: #zpracujeme posledni lexem
                    match_result = self.match_token()
                    if match_result == TokenType.UNDEFINED:
                        break
                new_token = Token(TokenType.EOF, '') #reprezentace EOF
                self.tokens.append(new_token) #pridani EOF tokenu do listu tokenu
                break
            elif self.current_char == ' ' or self.current_char == '\n':
                if self.current_lexem: #pokud nejaky lexem vubec existuje
                    match_result = self.match_token()
                    if match_result == TokenType.UNDEFINED:
                        break
                match self.current_char:
                    case '\n':
                        nl_token = Token(TokenType.EOL, '\n')
                        self.tokens.append(nl_token)
                self.get_next_char()
            elif self.current_char == '#': #resime kvuli moznosti mit pred komentarem mezeru ci nikoli
                if self.current_lexem:
                    if self.match_token() == TokenType.UNDEFINED:
                        break
                self.append_char_to_lexem(self.current_char)   
                self.get_next_char()
            else:
                self.append_char_to_lexem(self.current_char) #pokud nacteme znak, pridame jej do aktualne tvoreneho lexemu
                self.get_next_char()
        if self.tokens[-1].TokenType != TokenType.EOF:
            raise EXC_OTHER

#trida token listu a metody implementovane nad nim
class TokenList:
    def __init__(self, tokens: list):
        self.token_list = tokens #vlozime list tokenu, ktery dostaneme z lexikalni analyzy
        self.current_index = 0 #pro indexaci a moznou kontrolu zasahu mimo list
        self.active_token = self.token_list[0] #nastavime prvni prvek na aktivni
        self.previous_token = None #predchozi token pro moznost kontroly kontextu 
        self.active_list = True
        
    def next_token(self) -> bool:
        if self.current_index < len(self.token_list) - 1: #pokud jeste nejsme mimo list tokenu
            self.previous_token = self.token_list[self.current_index] #nastavime novy predchozi token
            self.current_index += 1 #zvysime index
            self.active_token = self.token_list[self.current_index] #nastavime dalsi token za aktivni
        else:
            self.active_list = False
        
        #metoda urcujici zdali jsme neprosli vsechny tokeny v listu
    def is_active(self) -> bool:
        return self.active_list == True