"""
            Analyzator kodu v IPPcode24 (Modul implementujici generator vystupniho kodu)

@file       modules/CodeGen.py       
@author     Machala Roman (xmacha86)
@brief      Modul je rizen syntaktickou analyzou. Kod je generovan v prubehu syntakticke kontroly a po jeji uspesnem ukonceni je vypsan na STDOUT.
"""

import xml.etree.ElementTree as ET
import xml.dom.minidom as MN
import re
from .LexicalAnalysis import Token, TokenType
from .definitions import *


"""

"""
class CodeGen():
    def __init__(self):
        self.root = ET.Element('program', language = "IPPcode24")
        self.order = 1
        self.current_param_count = 1
        self.current_param = None
        self.current_instruction = None
        
    #metoda ktera prida instrukci se spravnym order do vysledneho XML stromu
    def add_instruction(self, oper_code: str):
        self.current_instruction = ET.SubElement(self.root, "instruction", order = str(self.order), opcode=oper_code.upper())
        self.order += 1
        self.current_param_count = 1
        
    #metoda pridavajici promennou k posledni instrukci (univerzalni pro symb a var)
    def add_var_const(self, param: Token):
        param_type = None
        param_name = None
        match param.TokenType:
            case TokenType.INT_CONST | TokenType.STR_CONST | TokenType.BOOL_CONST | TokenType.NIL_CONST:
                param_type = param.lexem.split('@')[0]
                param_name = param.lexem.split('@')[1]
            case TokenType.IDENTIFIKATOR:
                param_type = 'var'
                param_name = param.lexem
        if self.current_instruction != None:
            self.current_param = ET.SubElement(self.current_instruction, 'arg' + str(self.current_param_count), type=param_type)
            self.current_param.text = param_name
            self.current_param_count += 1
        else:
            raise EXC_INTERNAL
        
    #metoda pridavajici instrukci label do stromu XML
    def add_label(self, param: Token):
        if self.current_instruction != None:
            self.current_param = ET.SubElement(self.current_instruction, 'arg' + str(self.current_param_count), type='label')
            self.current_param.text = param.lexem
            self.current_param_count += 1
        else:
            raise EXC_INTERNAL
        
    #metoda pridavajici TYPE do stromu XML
    def add_type(self, param: Token):
        if self.current_instruction != None:
            self.current_param = ET.SubElement(self.current_instruction, 'arg' + str(self.current_param_count), type='type')
            self.current_param.text = param.lexem
            self.current_param_count += 1
        else:
            raise EXC_INTERNAL
        
    #metoda vypisujici vyslednou XML programu na STDOUT
    def print_code(self):
        xml_string = ET.tostring(self.root, encoding='UTF-8')
        intendet_xml = MN.parseString(xml_string).toprettyxml(indent='\t', encoding='UTF-8')
        decoded_xml = intendet_xml.decode('UTF-8')
        decoded_xml = re.sub('\n+$', '', decoded_xml)
        print(decoded_xml, end='')