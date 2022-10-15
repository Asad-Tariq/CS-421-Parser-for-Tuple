from lexer import *
from parser_spec import *
import re

class Parser:

    def __init__(self, token_list, symbol_table) -> None:
        self.token_list = token_list
        self.symbol_table = symbol_table
        self.token_index = 0
        self.current_token = self.token_list[self.token_index]
        self.current_function = ""
        self.parser_trace = []

    def __updateTokens(self):
        tok = self.__checkToken()
        peek_tok = self.__peekToken()
        return tok, peek_tok

    def __program(self):
        print("IN PROGRAM")
        tok, peek_tok = self.__updateTokens()
        if tok[0] in firstSet["program"]:
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.current_function = tok[1]
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "(>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["paramList"]:
                self.__paramList()
                print("IN PROGRAM")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ")>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "{>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.parser_trace.append("In " + re.search("(.+?),", self.symbol_table[int(self.current_function[:-1])]).group(1) + "()")
            if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
                self.__stmts()
                print("IN PROGRAM")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "}>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.parser_trace.append("Exiting " + re.search("(.+?),", self.symbol_table[int(self.current_function[:-1])]).group(1) + "()")
            if peek_tok in followSet["program"]:
                self.parser_trace.append("EOF")
                return
            
        elif tok in followSet["program"] or peek_tok in followSet["program"]:
            self.parser_trace.append("EOF")
            return

        if tok[0] not in firstSet["program"] or tok[1] not in firstSet["program"]:
            self.parser_trace.append("Parsing Error!")
            return

    def __paramList(self):
        print("IN PARAMLIST")
        tok, peek_tok = self.__updateTokens()
        if tok[0] in firstSet["paramList"]:
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["pList"]:
                self.__pList()
                print("IN PARAMLIST")
                tok, peek_tok = self.__updateTokens()

        if tok[1] in followSet["paramList"]:
            return 

        if tok[0] not in firstSet["paramList"] and tok[1] not in firstSet["paramList"]:
            self.parser_trace.append("Parsing Error!")
            return

    def __pList(self):
        print("IN PLIST")
        tok, peek_tok = self.__updateTokens()
        if tok[1] in firstSet["pList"]:
            if tok[1] == ",>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["pList"]:
                self.__pList()
        
        elif tok[1] in followSet["pList"]:
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __stmts(self):
        print("IN STMTS")
        tok, peek_tok = self.__updateTokens()
        if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
            if tok[0] in firstSet["stmtsPrime"] or tok[1] in firstSet["stmtsPrime"]:
                self.__stmtsPrime()
                print("IN STMTS")
                tok, peek_tok = self.__updateTokens()
            else:
                self.parser_trace.append("Parsing Error!")
                return
        
        elif tok[1] in followSet["stmts"]:
            self.parser_trace.append("matched <" + tok[1])
            self.token_index += 1
            self.__nextToken()
            print("IN STMTS")
        
        elif "epsilon" in firstSet["stmts"] and tok[1] not in firstSet["stmts"] and tok[0] not in firstSet["stmts"]:
            self.__stmts()
            print("IN STMTS")
            tok, peek_tok = self.__updateTokens()
        
        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __stmtsPrime(self):
        print("IN STMTSPRIME")
        tok, peek_tok = self.__updateTokens()
        if tok[0] in firstSet["stmtsPrime"] or tok[1] in firstSet["stmtsPrime"]:
            if tok[0] in firstSet["decStmts"]:
                self.__decStmt()
                tok, peek_tok = self.__updateTokens()
                self.__stmtsPrime()
            if tok[0] in firstSet["assignStmt"]:
                self.__assignStmt()
                tok, peek_tok = self.__updateTokens()
                self.__stmtsPrime()
            if tok[1] in firstSet["forStmt"]:
                self.__forStmt()
                tok, peek_tok = self.__updateTokens()
                self.__stmtsPrime()
            if tok[1] in firstSet["ifStmt"]:
                self.__ifStmt()
                tok, peek_tok = self.__updateTokens()
                self.__stmtsPrime()
            if tok[1] in firstSet["returnStmt"]:
                self.__returnStmt()
                tok, peek_tok = self.__updateTokens()
                self.__stmtsPrime()
            else:
                return

        elif tok[1] in followSet["stmtsPrime"]:
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __decStmt(self):
        print("IN DECSTMT")
        tok, peek_tok = self.__updateTokens()
        if tok[0] in firstSet["decStmts"]:
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["optionalAssign"]:
                self.__optionalAssign()
                print("IN DECSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["list"]:
                self.__list()
                print("IN DECSTMT")
                tok, peek_tok = self.__updateTokens()

        elif tok[0] in followSet["decStmts"] or tok[1] in followSet["decStmts"]:
            # print("matched <" + tok[1])
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __list(self):
        print("IN LIST")
        tok, peek_tok = self.__updateTokens()
        if tok[1] in firstSet["list"]:
            if tok[1] == ",>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["optionalAssign"]:
                self.__optionalAssign()
                print("IN DECSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["list"]:
                self.__list()
            else:
                return
        
        elif tok[0] in followSet["list"]:
            # print("matched <" + tok[0] + ">")
            return

        elif tok[1] in followSet["list"]:
            # print("matched <" + tok[1])
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __optionalAssign(self):
        print("IN OPTIONALASSIGN")
        tok, peek_tok = self.__updateTokens()
        if tok[1] in firstSet["optionalAssign"]:
            self.parser_trace.append("matched <" + tok[1])
            self.token_index += 1
            self.__nextToken()
            tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN OPTIONALASSIGN")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            else:
                return
        
        elif tok[0] in followSet["optionalAssign"]:
            # print("matched <" + tok[0] + ">")
            return

        elif tok[1] in followSet["optionalAssign"]:
            # print("matched <" + tok[1])
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __assignStmt(self):
        print("IN ASSIGNSTMT")
        tok, peek_tok = self.__updateTokens()
        if tok[0] in firstSet["assignStmt"]:
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "=>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN ASSIGNSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()

        elif tok[0] in followSet["assignStmt"]:
            # print("matched <" + tok[0] + ">")
            return

        elif tok[1] in followSet["assignStmt"]:
            # print("matched <" + tok[1])
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __expr(self):
        print("IN EXPR")
        tok, peek_tok = self.__updateTokens()
        if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
            if tok[0] in firstSet["t"] or tok[1] in firstSet["t"]:
                self.__t()
                print("IN EXPR")
            if tok[1] in firstSet["ePrime"]:
                self.__ePrime()
                print("IN EXPR")
            if "epsilon" in firstSet["ePrime"] and tok[1] not in firstSet["ePrime"]:
                self.__ePrime()
                print("IN EXPR")

        elif tok[0] in followSet["expr"]:
            # print("matched <" + tok[0] + ">")
            return

        elif tok[1] in followSet["expr"]:
            # print("matched <" + tok[1])
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __ePrime(self):
        print("IN EPRIME")
        tok, peek_tok = self.__updateTokens()
        if len(tok) == 1:
            if tok[0][1:] in firstSet["ePrime"]:
                if tok[0][1:] == "+>":
                    self.parser_trace.append("matched <" + tok[0][1:])
                    self.token_index += 1
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
                if tok[0][1:] in firstSet["t"] or tok[0] in firstSet["t"]:
                    self.__t()
                    print("IN EPRIME")
                    tok, peek_tok = self.__updateTokens()
                if tok[1] in firstSet["ePrime"]:
                    self.__ePrime()
                    tok, peek_tok = self.__updateTokens()
                else:
                    return

        elif len(tok) == 2:
            if tok[0] in firstSet["ePrime"]:
                if tok[0] == "+>":
                    self.parser_trace.append("matched <" + tok[0][1:])
                    self.token_index += 1
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
                if tok[0] in firstSet["t"]:
                    self.__t()
                    print("IN EPRIME")
                    tok, peek_tok = self.__updateTokens()
                if tok[1] in firstSet["ePrime"]:
                    self.__ePrime()
                else:
                    return

        elif tok[0][1:] in followSet["ePrime"]:
            # print("matched <" + tok[0] + ">")
            return

        elif tok[1] in followSet["ePrime"]:
            # print("matched <" + tok[1])
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __t(self):
        print("IN T")
        tok, peek_tok = self.__updateTokens()
        if tok[0] in firstSet["t"] or tok[1] in firstSet["t"]:
            if tok[0] in firstSet["f"] or tok[1] in firstSet["f"]:
                # self.token_index += 1
                # self.__nextToken()
                self.__f()
                tok, peek_tok = self.__updateTokens()
                print("IN T")

            if len(tok) == 2:
                if tok[1] in firstSet["tPrime"]:
                    # self.__nextToken()
                    # tok, peek_tok = self.__updateTokens()
                    self.__tPrime()
                    print("IN T")
                    tok, peek_tok = self.__updateTokens()

            if "epsilon" in firstSet["tPrime"] and tok[0] not in firstSet["tPrime"]:
                self.__tPrime()
                print("IN T")

        elif tok[0] in followSet["t"]:
            return

        elif tok[1] in followSet["t"]:
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __tPrime(self):
        print("IN TPRIME")
        tok, peek_tok = self.__updateTokens()
        if len(tok) == 2:
            if tok[1] in firstSet["tPrime"]:
                if tok[1] == "*>":
                    self.parser_trace.append("matched <" + tok[1])
                    self.token_index += 1
                    self.__nextToken()
                if tok[0] in firstSet["f"] or tok[1] in firstSet["f"]:
                    self.__f()
                    print("IN TPRIME")
                    tok, peek_tok = self.__updateTokens()
                if tok[1] in firstSet["tPrime"]:
                    self.__tPrime()
                    print("IN TPRIME")
                else:
                    return

        elif tok[0][1:] in followSet["tPrime"]:
            # print("matched <" + tok[0] + ">")
            return
        
        elif tok[1] in followSet["tPrime"]:
            # print("matched <" + tok[1])
            return
        
        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __f(self):
        print("IN F")
        tok, peek_tok = self.__updateTokens()
        if tok[0] in firstSet["f"] or tok[1] in firstSet["f"]:
            if tok[1] == "(>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                    # self.token_index += 1
                    # self.__nextToken()
                    self.__expr()
                    print("IN F")
                    # tok, peek_tok = self.__updateTokens()
                if tok[1] == ")>":
                    self.parser_trace.append("matched <" + tok[1])
                    self.token_index += 1
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()

        elif tok[0] in followSet["f"]:
            # print("matched <" + tok[0] + ">")
            return

        elif tok[1] in followSet["f"]:
            # print("matched <" + tok[1])
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __forStmt(self):
        print("IN FORSTMT")
        tok, peek_tok = self.__updateTokens()
        if tok[1] in firstSet["forStmt"]:  
            if tok[1] == "for>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "(>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["type"]:
                self.__type()
                print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if "epsilon" in firstSet["type"] and tok[1] not in firstSet["type"]:
                self.__type()
                print("IN FORSTMT")
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                # self.token_index += 1
                # self.__nextToken()
                self.__expr()
                print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
                # print("tok in forStmt", tok)
                # print("peek_tok in forStmt", peek_tok)
            if tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                # self.token_index += 1
                # self.__nextToken()
                self.__expr()
                print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<rel_op":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                # self.token_index += 1
                # self.__nextToken()
                # tok, peek_tok = self.__updateTokens()
            if tok[0] == "<+>" and peek_tok == "<+>":
                self.parser_trace.append("matched " + tok[0][0:2] + peek_tok[1:2] + ">")
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                # print("tok in forStmt", tok)
                # print("peek_tok in forStmt", peek_tok)
            if tok[1] == ")>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "{>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                # print("tok in forStmt - 2", tok)
                # print("peek_tok in forStmt - 2", peek_tok)
            if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
                self.__stmts()
                print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "}>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
        
        elif tok[0] in followSet["forStmt"]:
            # print("matched <" + tok[0] + ">")
            return

        elif tok[1] in followSet["forStmt"]:
            # print("matched <" + tok[1])
            return
        
        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __type(self):
        print("IN TYPE")
        tok, peek_tok = self.__updateTokens()
        if tok[0] in firstSet["type"]:
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            else:
                return

        elif tok[0] in followSet["type"]:
            # print("matched <" + tok[1])
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __ifStmt(self):
        print("IN IFSTMT")
        tok, peek_tok = self.__updateTokens()
        if tok[1] in firstSet["ifStmt"]:
            if tok[1] == "if>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "(>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN IFSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<rel_op":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN IFSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ")>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "{>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
                self.__stmts()
                print("IN IFSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "}>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["optionalElse"]:
                self.__optionalElse()
                print("IN IFSTMT")
                tok, peek_tok = self.__updateTokens()

        elif tok[0] in followSet["ifStmt"]:
            # print("matched <" + tok[0] + ">")
            return

        elif[1] in followSet["ifStmt"]:
            # print("matched <" + tok[1])
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __optionalElse(self):
        print("IN OPTIONALELSE")
        tok, peek_tok = self.__updateTokens()
        if tok[1] in firstSet["optionalElse"]:
            if tok[1] == "else>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "{>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
                self.__stmts()
                print("IN OPTIONALELSE")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "}>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            else:
                return

        elif tok[0] in followSet["optionalElse"]:
            # print("matched <" + tok[0] + ">")
            return

        elif tok[1] in followSet["optionalElse"]:
            # print("matched <" + tok[1])
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return

    def __returnStmt(self):
        print("IN RETURNSTMT")
        tok, peek_tok = self.__updateTokens()
        if tok[1] in firstSet["returnStmt"]:
            if tok[1] == "return>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN RETURNSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.token_index += 1
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()

        elif tok[0] in followSet["returnStmt"]:
            # print("matched <" + tok[0] + ">")
            return

        elif tok[1] in followSet["returnStmt"]:
            # print("matched <" + tok[1])
            return

        else:
            self.parser_trace.append("Parsing Error!")
            return


    def __checkToken(self):
        return self.current_token.split(", ")

    def parseToken(self):
        self.__program()
        return self.parser_trace

    def __peekToken(self):
        if self.token_index + 1 >= len(self.token_list):
            return "<$>"
        return self.token_list[self.token_index + 1]

    def __nextToken(self):
        if self.token_index < len(self.token_list):
            self.current_token = self.token_list[self.token_index]