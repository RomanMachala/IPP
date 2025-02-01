"""
            Analyzator kodu v IPPcode24 (Modul implementujici STATP rozsireni)

@file       modules/Statistics.py       
@author     Machala Roman (xmacha86)
@brief      Modul je rizen syntaktickou analyzou. Stara se o spravnou vstupni kombinaci parametru. Ocekava od syntakticke analyzy dane parametry
            jednotlivych statistik a nasledne se stara o jejich spravne zapsani. Dale kontroluje duplicitu souboru pro vypis statistik
"""

from .definitions import *
import sys
import os
import re


"""
    Trida zpracovavajici rozsireni STATP. Zajistuje spravnou kombinaci parametru. Ocekava hodnoty jednotlivych statistik od syntakticke analyzy. Nakonec se stara o jejich
    zpracovani a vypis do vystupniho souboru.
"""
class Statistics:
    def __init__(self):
        self.list_of_params = sys.argv #ziskame vsechny parametry prikazove radky
        self.stat = False #implicitne neni pritomen --stat parametr
        self.stat_count = 0
        self.list_of_files = list() #prazdny list pro uchovani vsech souboru pro vypis statistik
        self.d_list_of_switches = list() #prazdny list listu pro prepinace --stat
        #(kazdy --stat bude mit svuj list, ve kterem budou ulozeny ktere statistiky prijdou vytisknout) 
    
    #zkontroluje, zda je pritomen help
    def check_for_help(self):
        if '--help' in self.list_of_params and len(self.list_of_params) == 2:
            help()
            sys.exit(CORRECT)
        elif '--help' in self.list_of_params and len(self.list_of_params) > 2:
            sys.exit(PARAM_ERROR)
            
    #metoda parsujici ostatni parametry 
    def parse_other_params(self):
        #help je jiz vyresen, nemusime se jiz znovu na nej dotazovat
        for param in self.list_of_params: #projdeme parametr po parametru
            if param.startswith('--stats='): #pokud parametr zacina na --stats=
                self.stat = True #nastavime, ze parametr --stats je pritomen
                self.stat_count += 1
                file_output = param.split('=')[1] #ziskame cestu souboru
                self.list_of_files.append(file_output) #pridame soubor do seznamu listu
                empty_list = list()
                self.d_list_of_switches.append(empty_list) #vlozeni listu pro uchovani prepinacu
            elif re.match(r'--loc$|--labels$|--jumps$|--fwjumps$|--backjumps$|--badjumps$|--frequent$|--eol$|--comments$', param): #vyber dane statistiky
                if not self.stat: #pokud neni alespon jeden --stat
                    sys.exit(PARAM_ERROR)
                else: #jinak parsneme argumenty
                    match param:
                        case '--loc':
                            self.d_list_of_switches[self.stat_count - 1].append(StatType.LOC)
                        case '--labels':
                            self.d_list_of_switches[self.stat_count - 1].append(StatType.LABELS)
                        case '--jumps':
                            self.d_list_of_switches[self.stat_count - 1].append(StatType.JUMPS)
                        case '--fwjumps':
                            self.d_list_of_switches[self.stat_count - 1].append(StatType.FWJUMPS)
                        case '--backjumps':
                            self.d_list_of_switches[self.stat_count - 1].append(StatType.BACKJUMPS)
                        case '--badjumps':
                            self.d_list_of_switches[self.stat_count - 1].append(StatType.BADJUMPS)
                        case '--frequent':
                            self.d_list_of_switches[self.stat_count - 1].append(StatType.FREQUENT)
                        case '--eol':
                            self.d_list_of_switches[self.stat_count - 1].append(StatType.EOL)
                        case '--comments':
                            self.d_list_of_switches[self.stat_count - 1].append(StatType.COMMENTS)
            elif param.startswith('--print='): #pokud je pritomen prepinac print
                string_to_print = param.split('=')[1]
                self.d_list_of_switches[self.stat_count - 1].append(string_to_print) #pridani strignu pro vypis do souboru
            elif param == 'parse.py':
                continue
            else:
                sys.exit(PARAM_ERROR)
    
    #metoda kontrolujici spravnost zadanych souboru, jejich duplicitu atd
    def check_files(self):
        absoluted_path_files = [os.path.abspath(file_path) for file_path in self.list_of_files]
        final_files = list()
        for file in absoluted_path_files:
            if file not in final_files:
                final_files.append(file)
            else:
                sys.exit(DUPLICITE_FILES)

        self.list_of_files = final_files

    #metoda pro vypis statistik do vystupnich souboru
    def print_statisctis(self, opcodes: list, labels_all: list, jump_backwards: int, jump_not_defined: list, loc: int):
        
        stat_loc = loc
        stat_comments = 0
        stat_labels = len(labels_all)
        stat_jumps = 0
        stat_fw_jumps = 0
        stat_bw_jumps = jump_backwards
        stat_bad_jumps = 0
        stat_frequent = None

        num_of_instruc = {} #slovnik uchovavajici celkovy pocet instrukci
        
        for instr in opcodes: #spocitame instrukce, jake se vyskytuji v program
            if instr in [TokenType.KW_JUMP, TokenType.KW_JUMPIFEQ, TokenType.KW_JUMPIFNEQ, TokenType.KW_RETURN, TokenType.KW_CALL]:
                stat_jumps += 1 #counter pro skoky
            if instr == TokenType.COMMENT:
                stat_comments += 1 #counter pro komentare
            if instr in num_of_instruc: #tvorba slovniku jednoltlivych instrukci a jejich poctu
                num_of_instruc[instr] += 1
            else:
                num_of_instruc[instr] = 1

        for label in jump_not_defined[:]:
            if label in labels_all:
                stat_fw_jumps += 1
                jump_not_defined.remove(label)

        stat_bad_jumps = len(jump_not_defined) #nedefinovane navesti, josu ta, ktera zbyla
        """
            Syntakticka analyza kontroluje skoky dozadu. Pokud se vyskytne skok na navesti, ktere jeste nebylo definovano, je ulozeno zde.
            Ve Statistics tride se zjisti, zdali je navesti neobjevilo pozdeji, pokud ano = skok dopredu, jinak nedefinovane navesti.
        """
        
        #nejvice opakovana frekvence (cislo)
        max_value = 0
        if num_of_instruc: #pokud vubec nejake instrukce jsou
            max_value = max(num_of_instruc.values())
    

        frequent = [inst for inst, times in num_of_instruc.items() if times == max_value] #ziskame vsechny s maximalnim poctem
        stat_frequent = sorted(frequent) #serazene instrukce abecedne vzestupne

        #pro kazdy soubor proved:
        for i in range(len(self.list_of_files)):
            with open(self.list_of_files[i], 'w') as file: #otevri soubor
                for stat in self.d_list_of_switches[i]: #pro kazdy switch/stat parametr pro dany soubor vypis jeho hodnotu
                    match stat:
                        case StatType.LOC:
                            file.write(f'{stat_loc}\n')
                        case StatType.COMMENTS:
                            file.write(f'{stat_comments}\n')
                        case StatType.LABELS:
                            file.write(f'{stat_labels}\n')
                        case StatType.JUMPS:
                            file.write(f'{stat_jumps}\n')
                        case StatType.FWJUMPS:
                            file.write(f'{stat_fw_jumps}\n')
                        case StatType.BACKJUMPS:
                            file.write(f'{stat_bw_jumps}\n')
                        case StatType.BADJUMPS:
                            file.write(f'{stat_bad_jumps}\n')
                        case StatType.FREQUENT: 
                            for j in range(len(stat_frequent)):
                                if stat_frequent[j] == TokenType.COMMENT:
                                    continue
                                temp = stat_frequent[j]
                                if stat_frequent[j].startswith('KW_'): #instrukce jsou ulozeny jako KW_OPCODE, protoze se pouzia TokenType ne nacteny lexem
                                    #neni treba prevadet na velke pismena (pokud na vstupu nezalezi na veliksoti pismen), je treba odstranit tuto predponu
                                    temp = stat_frequent[j].split('_')[1]
                                if j < len(stat_frequent) - 1:
                                    file.write(f'{temp}, ')
                                else:
                                    file.write(f'{temp}\n')
                        case StatType.EOL:
                            file.write('\n')
                        case _: #pro statistiku --print (v seznamu switchu se ulozi samotny retezec pro vypis)
                            file.write(f'{stat}\n')

        