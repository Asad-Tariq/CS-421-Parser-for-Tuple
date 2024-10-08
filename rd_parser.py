from lexer import *
from parser_spec import *
from typing import Dict, Tuple, List
import re


class Parser:
    """A recursive descent parser."""

    def __init__(self, token_list: List[str], symbol_table: Dict[int, str]) -> None:
        """Initializes the parser with the token stream from the lexer and the
        symbol table.

        Args:
        - self: this parser, the one to create. Mandatory object reference.
        - token_list: the token stream passed from the lexer.
        - symbol_table: the maintained symbol table.

        Returns:
        None.
        """

        self.token_list = token_list
        self.symbol_table = symbol_table
        self.token_index = 0
        self.current_token = self.token_list[self.token_index]
        self.current_function = ""
        self.parser_trace = []
        self.error_stream = {}
        self.line_count = 0

    def __checkToken(self) -> List[str]:
        """Returns the lexical unit and attribute of the current token.

        Args:
        - self: mandatory object reference.

        Returns:
        A split representation of the current token.
        """

        return self.current_token.split(", ")

    def __peekToken(self) -> str:
        """Returns the lookahead token. If the token stream has been parsed then
        the End of Stream token is returned.

        Args:
        - self: mandatory object reference.

        Returns:
        The lookahead token.
        """

        if self.token_index + 1 >= len(self.token_list):
            return "<$>"  # EOS token
        return self.token_list[self.token_index + 1]  

    def __nextToken(self) -> None:
        """Updates the current token.

        Args:
        - self: mandatory object reference.

        Returns:
        The lookahead token.
        """

        # increment pointer
        self.token_index += 1

        # upadate token if within bounds
        if self.token_index < len(self.token_list):
            self.current_token = self.token_list[self.token_index]

    def __updateTokens(self) -> Tuple[List[str], str]:
        """Returns the lexical unit and attribute of the current token in 
        addition to, the lookahead

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        tok = self.__checkToken()
        peek_tok = self.__peekToken()
        tok, peek_tok = self.__skipNewLine(tok, peek_tok)

        return tok, peek_tok

    def __skipNewLine(self, tok, peek_tok) -> Tuple[List[str], str]:
        """Skips the new line token.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        if tok[0] == "<newline>":
            self.__nextToken()
            tok, peek_tok = self.__updateTokens()
            self.line_count += 1
        
        return tok, peek_tok
    
    def __recordingErrors(self, tok, peek_tok) -> Tuple[List[str], str]:
        """Records the error and returns the next token.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        self.parser_trace.append("Parsing Error!")
        error = "Token " + tok[0] + ", " + tok[1] + " not expected in program"
        try:
            self.error_stream[self.line_count].append(error)
        except KeyError:
            self.error_stream[self.line_count] = [error]
        
        # The panic recovery system
        self.__nextToken()
        tok, peek_tok = self.__updateTokens()

        return tok, peek_tok
    
    def __program(self) -> None:
        """The production rules for the 'Program' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN PROGRAM")
        tok, peek_tok = self.__updateTokens()
        print(tok, peek_tok)

        if tok[0] in firstSet["program"]:
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.current_function = tok[1]
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "(>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["paramList"]:
                self.__paramList()
                print("IN PROGRAM")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ")>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "{>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.parser_trace.append("In " + re.search("(.+?),", self.symbol_table[int(self.current_function[:-1])]).group(1) + "()")
            if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
                self.__stmts()
                print("IN PROGRAM")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "}>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.parser_trace.append("Exiting " + re.search("(.+?),", self.symbol_table[int(self.current_function[:-1])]).group(1) + "()")
            if peek_tok in followSet["program"]:
                self.parser_trace.append("EOF")
                return
            
        if tok[0] in followSet["program"] or peek_tok in followSet["program"]:
            self.parser_trace.append("EOF")
            return

        if tok[0] not in firstSet["program"] or tok[1] not in firstSet["program"]:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            self.__program()

    def __paramList(self) -> None:
        """The production rules for the 'ParamList' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN PARAMLIST")
        tok, peek_tok = self.__updateTokens()

        if tok[0] in firstSet["paramList"]:
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["pList"]:
                self.__pList()
                print("IN PARAMLIST")
                tok, peek_tok = self.__updateTokens()

        if tok[1] in followSet["paramList"]:
            return 

        if tok[0] not in firstSet["paramList"] and tok[1] not in firstSet["paramList"]:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __pList(self) -> None:
        """The production rules for the 'PList' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN PLIST")
        tok, peek_tok = self.__updateTokens()

        if tok[1] in firstSet["pList"]:
            if tok[1] == ",>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["pList"]:
                self.__pList()
        
        if tok[1] in followSet["pList"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __stmts(self) -> None:
        """The production rules for the 'Stmts' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

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
            
            self.__nextToken()
            print("IN STMTS")
        
        elif "epsilon" in firstSet["stmts"] and tok[1] not in firstSet["stmts"] and tok[0] not in firstSet["stmts"]:
            self.__stmts()
            print("IN STMTS")
            tok, peek_tok = self.__updateTokens()
        
        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __stmtsPrime(self) -> None:
        """The production rules for the "Stmts'" non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

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
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __decStmt(self) -> None:
        """The production rules for the 'DecStmts' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN DECSTMT")
        tok, peek_tok = self.__updateTokens()

        if tok[0] in firstSet["decStmts"]:
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["optionalAssign"]:
                self.__optionalAssign()
                print("IN DECSTMT")
                tok, peek_tok = self.__updateTokens()
            if len(tok) == 1:
                if tok[0] in firstSet["list"]:
                    self.__list()
                    print("IN DECSTMT")
                    tok, peek_tok = self.__updateTokens()
            if len(tok) == 2:
                if tok[1] in firstSet["list"]:
                    self.__list()
                    print("IN DECSTMT")
                    tok, peek_tok = self.__updateTokens()

        elif tok[0] in followSet["decStmts"] or tok[1] in followSet["decStmts"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __list(self) -> None:
        """The production rules for the 'List' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN LIST")
        tok, peek_tok = self.__updateTokens()

        if tok[1] in firstSet["list"]:
            if tok[1] == ",>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
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
            return

        elif tok[1] in followSet["list"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __optionalAssign(self) -> None:
        """The production rules for the 'OptionalAssign' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN OPTIONALASSIGN")
        tok, peek_tok = self.__updateTokens()

        if tok[1] in firstSet["optionalAssign"]:
            self.parser_trace.append("matched <" + tok[1])
            self.__nextToken()
            tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN OPTIONALASSIGN")
                tok, peek_tok = self.__updateTokens()
            if len(tok) == 1:
                if tok[0] == ";>":
                    self.parser_trace.append("matched <" + tok[1])
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
            elif len(tok) == 2:
                if tok[1] == ";>":
                    self.parser_trace.append("matched <" + tok[1])
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
            else:
                return
        
        elif tok[0] in followSet["optionalAssign"]:
            return

        elif tok[1] in followSet["optionalAssign"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __assignStmt(self) -> None:
        """The production rules for the 'AssignStmt' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN ASSIGNSTMT")
        tok, peek_tok = self.__updateTokens()

        if tok[0] in firstSet["assignStmt"]:
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if len(tok) == 2 and tok[1] == "=>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"]:
                self.__expr()
                print("IN ASSIGNSTMT")
                tok, peek_tok = self.__updateTokens()
            if len(tok) == 2 and tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN ASSIGNSTMT")
                tok, peek_tok = self.__updateTokens()
            if len(tok) == 2 and tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __expr(self) -> None:
        """The production rules for the 'Expr' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

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
            return

        elif tok[1] in followSet["expr"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __ePrime(self) -> None:
        """The production rules for the "Expr'" non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN EPRIME")
        tok, peek_tok = self.__updateTokens()

        if len(tok) == 1:
            if tok[0][1:] in firstSet["ePrime"]:
                if tok[0][1:] == "+>":
                    self.parser_trace.append("matched <" + tok[0][1:])
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
                if tok[0][1:] in firstSet["t"] or tok[0] in firstSet["t"]:
                    self.__t()
                    print("IN EPRIME")
                    tok, peek_tok = self.__updateTokens()
                if len(tok) == 1:
                    if tok[0] in firstSet["ePrime"]:
                        self.__ePrime()
                        tok, peek_tok = self.__updateTokens()
                if len(tok) == 2:
                    if tok[1] in firstSet["ePrime"]:
                        self.__ePrime()
                        tok, peek_tok = self.__updateTokens()
                else:
                    return

        elif len(tok) == 2:
            if tok[0] in firstSet["ePrime"]:
                if tok[0] == "+>":
                    self.parser_trace.append("matched <" + tok[0][1:])
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
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __t(self) -> None:
        """The production rules for the 'T' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN T")
        tok, peek_tok = self.__updateTokens()

        if tok[0] in firstSet["t"] or tok[1] in firstSet["t"]:
            if tok[0] in firstSet["f"] or tok[1] in firstSet["f"]:
                self.__f()
                tok, peek_tok = self.__updateTokens()
                print("IN T")

            if len(tok) == 2:
                if tok[1] in firstSet["tPrime"]:
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
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __tPrime(self) -> None:
        """The production rules for the "T'" non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN TPRIME")
        tok, peek_tok = self.__updateTokens()

        if len(tok) == 2:
            if tok[1] in firstSet["tPrime"]:
                if tok[1] == "*>":
                    self.parser_trace.append("matched <" + tok[1])
                    self.__nextToken()
                if tok[0] in firstSet["f"] or tok[1] in firstSet["f"]:
                    self.__f()
                    print("IN TPRIME")
                    tok, peek_tok = self.__updateTokens()
                if tok[1] in firstSet["tPrime"]:
                    self.__tPrime()
                    print("IN TPRIME")

        elif len(tok) == 1:
            if tok[0][1:] in firstSet["tPrime"]:
                if tok[0][1:] == "*>":
                    self.parser_trace.append("matched <" + tok[0][1:])
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
                if tok[0] in firstSet["f"]:
                    self.__f()
                    print("IN TPRIME")
                    tok, peek_tok = self.__updateTokens()
                if len(tok) == 2 and tok[1] in firstSet["tPrime"]:
                    self.__f()
                    print("IN TPRIME")
                    tok, peek_tok = self.__updateTokens()
                if tok[0][1:] in firstSet["tPrime"]:
                    self.__tPrime()
                    print("IN TPRIME")
                else:
                    return

        elif tok[0][1:] in followSet["tPrime"]:
            return
        
        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __f(self) -> None:
        """The production rules for the 'F' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN F")
        tok, peek_tok = self.__updateTokens()

        if tok[0] in firstSet["f"] or tok[1] in firstSet["f"]:
            if tok[1] == "(>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                    self.__expr()
                    print("IN F")
                if tok[1] == ")>":
                    self.parser_trace.append("matched <" + tok[1])
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                
        elif tok[0] in followSet["f"]:
            return

        elif tok[1] in followSet["f"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __forStmt(self) -> None:
        """The production rules for the 'ForStmt' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN FORSTMT")
        tok, peek_tok = self.__updateTokens()

        if tok[1] in firstSet["forStmt"]:  
            if tok[1] == "for>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "(>":
                self.parser_trace.append("matched <" + tok[1])
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
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<rel_op":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<+>" and peek_tok == "<+>":
                self.parser_trace.append("matched " + tok[0][0:2] + peek_tok[1:2] + ">")
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ")>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "{>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
                self.__stmts()
                print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "}>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
        
        elif tok[0] in followSet["forStmt"]:
            return

        elif tok[1] in followSet["forStmt"]:
            return
        
        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __type(self) -> None:
        """The production rules for the 'Type' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN TYPE")
        tok, peek_tok = self.__updateTokens()

        if tok[0] in firstSet["type"]:
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            else:
                return

        elif tok[0] in followSet["type"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __ifStmt(self) -> None:
        """The production rules for the 'IfStmt' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN IFSTMT")
        tok, peek_tok = self.__updateTokens()

        if tok[1] in firstSet["ifStmt"]:
            if tok[1] == "if>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "(>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN IFSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<rel_op":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN IFSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ")>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "{>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
                self.__stmts()
                print("IN IFSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "}>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["optionalElse"]:
                self.__optionalElse()
                print("IN IFSTMT")
                tok, peek_tok = self.__updateTokens()

        elif tok[0] in followSet["ifStmt"]:
            return

        elif[1] in followSet["ifStmt"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __optionalElse(self) -> None:
        """The production rules for the 'OptionalElse' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN OPTIONALELSE")
        tok, peek_tok = self.__updateTokens()

        if tok[1] in firstSet["optionalElse"]:
            if tok[1] == "else>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "{>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
                self.__stmts()
                print("IN OPTIONALELSE")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "}>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            else:
                return

        elif tok[0] in followSet["optionalElse"]:
            return

        elif tok[1] in followSet["optionalElse"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __returnStmt(self) -> None:
        """The production rules for the 'ReturnStmt' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        print("IN RETURNSTMT")
        tok, peek_tok = self.__updateTokens()
        if tok[1] in firstSet["returnStmt"]:
            if tok[1] == "return>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                print("IN RETURNSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()

        elif tok[0] in followSet["returnStmt"]:
            return

        elif tok[1] in followSet["returnStmt"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def parseToken(self) -> List[str]:
        """Public method that instigates the parsing.

        Args:
        - self: mandatory object reference.

        Returns:
        The output of the parser in the form of a trace of the syntax analysis.
        """

        self.__program()
        return self.parser_trace, self.error_stream
            