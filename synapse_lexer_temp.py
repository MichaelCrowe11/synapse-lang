"""
Lexer and Token definitions for Synapse Language
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

class TokenType(Enum):
    # Keywords
    HYPOTHESIS = "hypothesis"
    EXPERIMENT = "experiment"
    PARALLEL = "parallel"
    BRANCH = "branch"
    STREAM = "stream"
    REASON = "reason"
    CHAIN = "chain"
    PREMISE = "premise"
    DERIVE = "derive"
    CONCLUDE = "conclude"
    UNCERTAIN = "uncertain"
    OBSERVE = "observe"
    PROPAGATE = "propagate"
    CONSTRAIN = "constrain"
    EVOLVE = "evolve"
    PIPELINE = "pipeline"
    STAGE = "stage"
    FORK = "fork"
    PATH = "path"
    MERGE = "merge"
    EXPLORE = "explore"
    TRY = "try"
    FALLBACK = "fallback"
    ACCEPT = "accept"
    REJECT = "reject"
    SYMBOLIC = "symbolic"
    LET = "let"
    SOLVE = "solve"
    PROVE = "prove"
    USING = "using"
    
    # Quantum computing keywords
    QUANTUM = "quantum"
    CIRCUIT = "circuit"
    MEASURE = "measure"
    BACKEND = "backend"
    ALGORITHM = "algorithm"
    RUN = "run"
    WITH = "with"

    # Backend keywords
    SHOTS = "shots"
    NOISE_MODEL = "noise_model"
    SEED = "seed"
    IDEAL = "ideal"
    DEPOLARIZING = "depolarizing"
    P1Q = "p1q"
    P2Q = "p2q"
    READOUT = "readout"

    # Algorithm keywords
    PARAMETERS = "parameters"
    ANSATZ = "ansatz"
    COST_FUNCTION = "cost_function"
    OPTIMIZE = "optimize"

    # Gate names (as keywords for simplicity, parser can handle aliases)
    H = "h"
    X = "x"
    Y = "y"
    Z = "z"
    S = "s"
    SDG = "sdg"
    T = "t"
    TDG = "tdg"
    RX = "rx"
    RY = "ry"
    RZ = "rz"
    U = "u"
    CX = "cx"
    CNOT = "cnot"
    CZ = "cz"
    SWAP = "swap"
    ISWAP = "iswap"
    CCX = "ccx"
    TOFFOLI = "toffoli"
    CSWAP = "cswap"

    # Operators
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    POWER = "^"
    LESS_THAN = "<"
    GREATER_THAN = ">"
    EQUALS = "=="
    NOT_EQUALS = "!="
    AND = "&&"
    OR = "||"
    NOT = "!"
    UNCERTAINTY = "±"
    ARROW = "=>"
    BIND_OUTPUT = "->"
    CHANNEL_SEND = "<-"

    # Delimiters
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    COMMA = ","
    COLON = ":"
    SEMICOLON = ";"

    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"

    # Special
    EOF = "EOF"
    NEWLINE = "NEWLINE"

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

        self.keywords = {
            "hypothesis": TokenType.HYPOTHESIS,
            "experiment": TokenType.EXPERIMENT,
            "parallel": TokenType.PARALLEL,
            "branch": TokenType.BRANCH,
            "stream": TokenType.STREAM,
            "reason": TokenType.REASON,
            "chain": TokenType.CHAIN,
            "premise": TokenType.PREMISE,
            "derive": TokenType.DERIVE,
            "conclude": TokenType.CONCLUDE,
            "uncertain": TokenType.UNCERTAIN,
            "observe": TokenType.OBSERVE,
            "propagate": TokenType.PROPAGATE,
            "constrain": TokenType.CONSTRAIN,
            "evolve": TokenType.EVOLVE,
            "pipeline": TokenType.PIPELINE,
            "stage": TokenType.STAGE,
            "fork": TokenType.FORK,
            "path": TokenType.PATH,
            "merge": TokenType.MERGE,
            "explore": TokenType.EXPLORE,
            "try": TokenType.TRY,
            "fallback": TokenType.FALLBACK,
            "accept": TokenType.ACCEPT,
            "reject": TokenType.REJECT,
            "symbolic": TokenType.SYMBOLIC,
            "let": TokenType.LET,
            "solve": TokenType.SOLVE,
            "prove": TokenType.PROVE,
            "using": TokenType.USING,
            
            # Quantum computing keywords
            "quantum": TokenType.QUANTUM,
            "circuit": TokenType.CIRCUIT,
            "measure": TokenType.MEASURE,
            "backend": TokenType.BACKEND,
            "algorithm": TokenType.ALGORITHM,
            "run": TokenType.RUN,
            "with": TokenType.WITH,

            # Backend keywords
            "shots": TokenType.SHOTS,
            "noise_model": TokenType.NOISE_MODEL,
            "seed": TokenType.SEED,
            "ideal": TokenType.IDEAL,
            "depolarizing": TokenType.DEPOLARIZING,
            "p1q": TokenType.P1Q,
            "p2q": TokenType.P2Q,
            "readout": TokenType.READOUT,

            # Algorithm keywords
            "parameters": TokenType.PARAMETERS,
            "ansatz": TokenType.ANSATZ,
            "cost_function": TokenType.COST_FUNCTION,
            "optimize": TokenType.OPTIMIZE,

            # Gate names
            "h": TokenType.H, "x": TokenType.X, "y": TokenType.Y, "z": TokenType.Z,
            "s": TokenType.S, "sdg": TokenType.SDG, "t": TokenType.T, "tdg": TokenType.TDG,
            "rx": TokenType.RX, "ry": TokenType.RY, "rz": TokenType.RZ, "u": TokenType.U,
            "cx": TokenType.CX, "cnot": TokenType.CNOT, "cz": TokenType.CZ,
            "swap": TokenType.SWAP, "iswap": TokenType.ISWAP,
            "ccx": TokenType.CCX, "toffoli": TokenType.TOFFOLI, "cswap": TokenType.CSWAP,
        }

    def current_char(self) -> Optional[str]:
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def peek_char(self, offset: int = 1) -> Optional[str]:
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]

    def advance(self) -> None:
        if self.position < len(self.source):
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def skip_whitespace(self) -> None:
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()

    def skip_comment(self) -> None:
        # Updated to handle '#' style comments as per recent examples
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
        elif self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()

    def read_number(self) -> Union[int, float]:
        start = self.position
        has_dot = False

        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break
                has_dot = True
            self.advance()
        
        num_str = self.source[start:self.position]
        if has_dot:
            return float(num_str)
        return int(num_str)

    def read_identifier(self) -> str:
        start = self.position

        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()

        return self.source[start:self.position]

    def read_string(self) -> str:
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        start = self.position

        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()  # Skip escape character
            self.advance()

        value = self.source[start:self.position]
        self.advance()  # Skip closing quote
        return value

    def tokenize(self) -> List[Token]:
        while self.position < len(self.source):
            self.skip_whitespace()
            self.skip_comment()

            if not self.current_char():
                break

            line = self.line
            column = self.column

            # Multi-character operators
            if self.current_char() == '=' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.EQUALS, "==", line, column))
            elif self.current_char() == '!' and self.peek_char() == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.NOT_EQUALS, "!=", line, column))
            elif self.current_char() == '&' and self.peek_char() == '&':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.AND, "&&", line, column))
            elif self.current_char() == '|' and self.peek_char() == '|':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.OR, "||", line, column))
            elif self.current_char() == '=' and self.peek_char() == '>':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.ARROW, "=>", line, column))
            elif self.current_char() == '-' and self.peek_char() == '>':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.BIND_OUTPUT, "->", line, column))
            elif self.current_char() == '<' and self.peek_char() == '-':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.CHANNEL_SEND, "<-", line, column))
            elif self.current_char() == '±':
                self.advance()
                self.tokens.append(Token(TokenType.UNCERTAINTY, "±", line, column))

            # Single character operators and delimiters
            elif self.current_char() == '=':
                self.advance()
                self.tokens.append(Token(TokenType.ASSIGN, "=", line, column))
            elif self.current_char() == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, "+", line, column))
            elif self.current_char() == '-':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, "-", line, column))
            elif self.current_char() == '*':
                self.advance()
                self.tokens.append(Token(TokenType.MULTIPLY, "*", line, column))
            elif self.current_char() == '/':
                self.advance()
                self.tokens.append(Token(TokenType.DIVIDE, "/", line, column))
            elif self.current_char() == '^':
                self.advance()
                self.tokens.append(Token(TokenType.POWER, "^", line, column))
            elif self.current_char() == '<':
                self.advance()
                self.tokens.append(Token(TokenType.LESS_THAN, "<", line, column))
            elif self.current_char() == '>':
                self.advance()
                self.tokens.append(Token(TokenType.GREATER_THAN, ">", line, column))
            elif self.current_char() == '!':
                self.advance()
                self.tokens.append(Token(TokenType.NOT, "!", line, column))
            elif self.current_char() == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LEFT_PAREN, "(", line, column))
            elif self.current_char() == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RIGHT_PAREN, ")", line, column))
            elif self.current_char() == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LEFT_BRACE, "{", line, column))
            elif self.current_char() == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RIGHT_BRACE, "}", line, column))
            elif self.current_char() == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LEFT_BRACKET, "[", line, column))
            elif self.current_char() == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RIGHT_BRACKET, "]", line, column))
            elif self.current_char() == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ",", line, column))
            elif self.current_char() == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ":", line, column))
            elif self.current_char() == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ";", line, column))
            elif self.current_char() == '\n':
                self.advance()
                # Don't add newline tokens if they are not significant
                # self.tokens.append(Token(TokenType.NEWLINE, "\\n", line, column))

            # Numbers
            elif self.current_char().isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, line, column))

            # Strings
            elif self.current_char() in '"\'':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, line, column))

            # Identifiers and keywords
            elif self.current_char().isalpha() or self.current_char() == '_':
                start_pos = self.position
                identifier = self.read_identifier()
                original_identifier = self.source[start_pos:self.position]
                token_type = self.keywords.get(identifier.lower(), TokenType.IDENTIFIER)
                
                value = original_identifier if token_type == TokenType.IDENTIFIER else identifier.lower()
                self.tokens.append(Token(token_type, value, line, column))

            else:
                # Skip unknown characters for now
                self.advance()

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
