"""
Synapse Language Lexer (packaged)
"""

from typing import Any, List, Optional, Union
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

    # Gate names (as keywords)
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
        self.tokens: List[Token] = []

        # keyword map
        self.keywords = {k.value: k for k in TokenType if k.value.isalpha() and k not in (TokenType.IDENTIFIER,)}

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
            if self.source[self.position] == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def skip_whitespace(self) -> None:
        while self.current_char() and self.current_char() in " \t\r":
            self.advance()

    def skip_comment(self) -> None:
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
        lexeme = self.source[start:self.position]
        return float(lexeme) if has_dot else int(lexeme)

    def read_identifier(self) -> str:
        start = self.position
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()
        return self.source[start:self.position]

    def read_string(self) -> str:
        quote = self.current_char()
        self.advance()
        start = self.position
        while self.current_char() and self.current_char() != quote:
            if self.current_char() == '\\':
                self.advance()
            self.advance()
        value = self.source[start:self.position]
        self.advance()  # closing quote
        return value

    def tokenize(self) -> List[Token]:
        while self.position < len(self.source):
            self.skip_whitespace()
            self.skip_comment()
            if self.position >= len(self.source):
                break
            line, col = self.line, self.column
            ch = self.current_char()

            # multi-char operators
            two = (ch or '') + (self.peek_char() or '')
            if two in {"==", "!=", "&&", "||", "=>", "->", "<-"}:
                mapping = {
                    "==": TokenType.EQUALS,
                    "!=": TokenType.NOT_EQUALS,
                    "&&": TokenType.AND,
                    "||": TokenType.OR,
                    "=>": TokenType.ARROW,
                    "->": TokenType.BIND_OUTPUT,
                    "<-": TokenType.CHANNEL_SEND,
                }
                self.advance(); self.advance()
                self.tokens.append(Token(mapping[two], two, line, col))
                continue

            if ch is None:
                break
            if ch == '\n':
                self.advance()
                continue
            single_map = {
                '=': TokenType.ASSIGN, '+': TokenType.PLUS, '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY, '/': TokenType.DIVIDE, '^': TokenType.POWER,
                '<': TokenType.LESS_THAN, '>': TokenType.GREATER_THAN, '!': TokenType.NOT,
                '(': TokenType.LEFT_PAREN, ')': TokenType.RIGHT_PAREN,
                '{': TokenType.LEFT_BRACE, '}': TokenType.RIGHT_BRACE,
                '[': TokenType.LEFT_BRACKET, ']': TokenType.RIGHT_BRACKET,
                ',': TokenType.COMMA, ':': TokenType.COLON, ';': TokenType.SEMICOLON,
            }
            if ch in single_map:
                self.advance()
                self.tokens.append(Token(single_map[ch], ch, line, col))
                continue
            if ch.isdigit():
                num = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, num, line, col))
                continue
            if ch in '"\'':
                s = self.read_string()
                self.tokens.append(Token(TokenType.STRING, s, line, col))
                continue
            if ch.isalpha() or ch == '_':
                ident_start = self.position
                ident = self.read_identifier()
                token_type = self.keywords.get(ident.lower(), TokenType.IDENTIFIER)
                value = self.source[ident_start:self.position] if token_type == TokenType.IDENTIFIER else ident.lower()
                self.tokens.append(Token(token_type, value, line, col))
                continue
            # unknown -> skip
            self.advance()
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
