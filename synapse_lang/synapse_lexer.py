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
    
    # Control flow keywords
    IF = "if"
    ELSE = "else"
    ELIF = "elif"
    WHILE = "while"
    FOR = "for"
    IN = "in"
    BREAK = "break"
    CONTINUE = "continue"
    RETURN = "return"

    # Additional keywords for compatibility
    FROM = "from"
    INTO = "into"
    THROUGH = "through"
    WHERE = "where"
    WHEN = "when"
    UNTIL = "until"
    VALUE = "value"
    MAP = "map"
    PREDICT = "predict"
    VALIDATE = "validate"
    SYNTHESIZE = "synthesize"
    ASSUME = "assume"
    SETUP = "setup"
    AUTO = "auto"
    COST = "cost"
    OPTIMIZER = "optimizer"
    UNCERTAINTY = "uncertainty"

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
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    AND = "&&"
    OR = "||"
    NOT = "!"
    ARROW = "=>"
    BIND_OUTPUT = "->"
    CHANNEL_SEND = "<-"
    DOT = "."
    PERCENT = "%"
    TILDE = "~"
    QUESTION = "?"

    # Mathematical operators for symbolic math
    INTEGRAL = "∫"
    DERIVATIVE = "∂"
    GRADIENT = "∇"
    INFINITY = "∞"
    SQRT = "√"
    THETA = "θ"
    PHI = "φ"
    PI = "π"
    SIGMA = "Σ"
    PRODUCT = "∏"
    LIMIT = "lim"
    PARTIAL = "∂"
    NABLA = "∇"
    
    # Additional operators for compatibility
    STAR = "*"
    SLASH = "/"
    EQUAL = "="
    EQUAL_EQUAL = "=="
    NOT_EQUAL = "!="
    PLUS_MINUS = "+-"
    UNCERTAINTY_OP = "±"

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
    INDENT = "INDENT"
    DEDENT = "DEDENT"


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
        self.indent_stack = [0]  # Stack to track indentation levels
        self.at_line_start = True  # Track if we're at the start of a line

        # keyword map - exclude single-letter gate names from general keywords
        # Gate names should only be recognized in quantum circuit context
        gate_types = {
            TokenType.H, TokenType.X, TokenType.Y, TokenType.Z,
            TokenType.S, TokenType.T, TokenType.U
        }
        self.keywords = {
            k.value: k for k in TokenType
            if k.value and k.value.isalpha() and k not in (TokenType.IDENTIFIER,) and k not in gate_types
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
            if self.source[self.position] == "\n":
                self.line += 1
                self.column = 1
                self.at_line_start = True
            else:
                self.column += 1
                if not self.source[self.position].isspace():
                    self.at_line_start = False
            self.position += 1

    def handle_indentation(self) -> None:
        """Handle indentation at the start of a line"""
        if not self.at_line_start:
            return

        indent_level = 0
        start_pos = self.position

        # Count spaces and tabs (convert tabs to 4 spaces)
        while self.current_char() and self.current_char() in " \t":
            if self.current_char() == " ":
                indent_level += 1
            elif self.current_char() == "\t":
                indent_level += 4
            self.advance()

        # If line is empty or comment, don't process indentation
        if self.current_char() in [None, '\n', '#'] or (self.current_char() == '/' and self.peek_char() == '/'):
            return

        current_indent = self.indent_stack[-1]
        line, col = self.line, 1

        if indent_level > current_indent:
            # Increase in indentation
            self.indent_stack.append(indent_level)
            self.tokens.append(Token(TokenType.INDENT, None, line, col))
        elif indent_level < current_indent:
            # Decrease in indentation - may need multiple DEDENT tokens
            while self.indent_stack and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, None, line, col))

            # Check for indentation error
            if not self.indent_stack or self.indent_stack[-1] != indent_level:
                raise SyntaxError(f"Indentation error at line {line}")

        self.at_line_start = False

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
            # Handle indentation at start of line
            if self.at_line_start:
                self.handle_indentation()

            self.skip_whitespace()
            self.skip_comment()
            if self.position >= len(self.source):
                break
            line, col = self.line, self.column
            ch = self.current_char()

            # multi-char operators
            two = (ch or '') + (self.peek_char() or '')
            if two in {"==", "!=", "&&", "||", "=>", "->", "<-", "<=", ">=", "+-"}:
                mapping = {
                    "==": TokenType.EQUALS,
                    "!=": TokenType.NOT_EQUALS,
                    "&&": TokenType.AND,
                    "||": TokenType.OR,
                    "=>": TokenType.ARROW,
                    "->": TokenType.BIND_OUTPUT,
                    "<-": TokenType.CHANNEL_SEND,
                    "<=": TokenType.LESS_EQUAL,
                    ">=": TokenType.GREATER_EQUAL,
                    "+-": TokenType.PLUS_MINUS,
                }
                self.advance(); self.advance()
                self.tokens.append(Token(mapping[two], two, line, col))
                continue

            if ch is None:
                break
            if ch == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', line, col))
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
                '.': TokenType.DOT, '%': TokenType.PERCENT, '~': TokenType.TILDE,
                '?': TokenType.QUESTION, '±': TokenType.UNCERTAINTY_OP,
                # Mathematical Unicode symbols
                '∫': TokenType.INTEGRAL, '∂': TokenType.DERIVATIVE, '∇': TokenType.GRADIENT,
                '∞': TokenType.INFINITY, '√': TokenType.SQRT, 'θ': TokenType.THETA,
                'φ': TokenType.PHI, 'π': TokenType.PI, 'Σ': TokenType.SIGMA, '∏': TokenType.PRODUCT,
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

        # Add DEDENT tokens for any remaining indentation at end of file
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, None, self.line, self.column))

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
