"""
            Analyzator kodu v IPPcode24 (hlavni telo)

@file       parse.py       
@author     Machala Roman (xmacha86)
@brief      Jedna se o analyzator kodu napsaneho v jazyce IPPcode24. Skript je slozen z nekolika modulu nachazejicich se ve slozce
            /modules. 
"""

import sys

from modules.definitions import *
from modules.LexicalAnalysis import TokenList, LexicalAnalyzer
from modules.Statistics import Statistics
from modules.SyntaxAnalysis import SyntaxAnalysis  


    #TODO jednotlive pravidla gramatiky jako samostatne metody, budou se volat 
if __name__ == '__main__':
   
    try:
        statistics = Statistics() 
        statistics.check_for_help() #pritomnost help
        statistics.parse_other_params() #kontrola parametru obecne
        statistics.check_files()
        lexical_analysis = LexicalAnalyzer() #konstrukce lex. analyzy
        
        lex_result = lexical_analysis.analyze() #provedeni samotne lex. analyzy
        token_list = TokenList(lexical_analysis.tokens)
        syntax_analysis = SyntaxAnalysis(token_list)
        syntax_analysis.parse_header()
        syntax_analysis.code.print_code()

        #vypis samotnych statistik
        statistics.print_statisctis(syntax_analysis.opcodes, syntax_analysis.labels_all, syntax_analysis.jumps_backward, syntax_analysis.jumps_not_defined, syntax_analysis.loc) 
        sys.exit(CORRECT) 
    except OtherError:
        sys.stderr.write('Other syntaktic error')
        sys.exit(OTHER_ERROR)
    except MissingHeaderError:
        sys.stderr.write('Missing header')
        sys.exit(MISSING_HEADER)
    except ErrorOperand:
        sys.stderr.write('Invalid operand')
        sys.exit(ERROR_OPERAND)
    except InternalError:
        sys.stderr.write('Internal error')
        sys.exit(INTERNAL_ERROR)