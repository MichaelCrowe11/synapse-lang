# Quantum-Net: Distributed Quantum Computing & Networking Language - Lexer
# Essential for building next-generation quantum internet and distributed quantum systems

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Network-specific keywords
    NETWORK = auto()
    NODE = auto()
    LINK = auto()
    CHANNEL = auto()
    PROTOCOL = auto()
    ROUTE = auto()
    ENDPOINT = auto()
    REPEATER = auto()

    # Quantum networking operations
    ENTANGLE = auto()
    TELEPORT = auto()
    SWAP = auto()
    PURIFY = auto()
    DISTILL = auto()
    DISTRIBUTE = auto()
    BROADCAST = auto()
    MULTICAST = auto()

    # Communication primitives
    SEND = auto()
    RECEIVE = auto()
    ESTABLISH = auto()
    CONNECT = auto()
    DISCONNECT = auto()
    SYNC = auto()
    ASYNC = auto()

    # Security & Cryptography
    QKD = auto()  # Quantum Key Distribution
    BB84 = auto()
    E91 = auto()
    AUTHENTICATE = auto()
    ENCRYPT = auto()
    VERIFY = auto()

    # Network topology
    TOPOLOGY = auto()
    STAR = auto()
    MESH = auto()
    RING = auto()
    TREE = auto()
    HYBRID = auto()

    # Resource management
    ALLOCATE = auto()
    RESERVE = auto()
    RELEASE = auto()
    SCHEDULE = auto()
    PRIORITY = auto()
    BANDWIDTH = auto()
    FIDELITY = auto()

    # Error handling
    CORRECT = auto()
    DETECT = auto()
    RETRY = auto()
    FAILOVER = auto()
    REDUNDANT = auto()

    # Timing and synchronization
    CLOCK = auto()
    LATENCY = auto()
    TIMEOUT = auto()
    WINDOW = auto()
    SEQUENCE = auto()

    # Standard tokens
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    OPERATOR = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    DOT = auto()
    ARROW = auto()
    DOUBLE_ARROW = auto()
    ASSIGN = auto()

    # Network operators
    PIPE = auto()  # |> for data flow
    PARALLEL = auto()  # || for parallel channels
    CASCADE = auto()  # >> for sequential operations

    # Special symbols
    AT = auto()  # @ for node addressing
    HASH = auto()  # # for channel ID
    DOLLAR = auto()  # $ for resource reference

    # Control flow
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    AWAIT = auto()

    # End of file
    EOF = auto()
    NEWLINE = auto()

@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int

class QuantumNetLexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

        # Keywords mapping
        self.keywords = {
            "network": TokenType.NETWORK,
            "node": TokenType.NODE,
            "link": TokenType.LINK,
            "channel": TokenType.CHANNEL,
            "protocol": TokenType.PROTOCOL,
            "route": TokenType.ROUTE,
            "endpoint": TokenType.ENDPOINT,
            "repeater": TokenType.REPEATER,
            "entangle": TokenType.ENTANGLE,
            "teleport": TokenType.TELEPORT,
            "swap": TokenType.SWAP,
            "purify": TokenType.PURIFY,
            "distill": TokenType.DISTILL,
            "distribute": TokenType.DISTRIBUTE,
            "broadcast": TokenType.BROADCAST,
            "multicast": TokenType.MULTICAST,
            "send": TokenType.SEND,
            "receive": TokenType.RECEIVE,
            "establish": TokenType.ESTABLISH,
            "connect": TokenType.CONNECT,
            "disconnect": TokenType.DISCONNECT,
            "sync": TokenType.SYNC,
            "async": TokenType.ASYNC,
            "qkd": TokenType.QKD,
            "bb84": TokenType.BB84,
            "e91": TokenType.E91,
            "authenticate": TokenType.AUTHENTICATE,
            "encrypt": TokenType.ENCRYPT,
            "verify": TokenType.VERIFY,
            "topology": TokenType.TOPOLOGY,
            "star": TokenType.STAR,
            "mesh": TokenType.MESH,
            "ring": TokenType.RING,
            "tree": TokenType.TREE,
            "hybrid": TokenType.HYBRID,
            "allocate": TokenType.ALLOCATE,
            "reserve": TokenType.RESERVE,
            "release": TokenType.RELEASE,
            "schedule": TokenType.SCHEDULE,
            "priority": TokenType.PRIORITY,
            "bandwidth": TokenType.BANDWIDTH,
            "fidelity": TokenType.FIDELITY,
            "correct": TokenType.CORRECT,
            "detect": TokenType.DETECT,
            "retry": TokenType.RETRY,
            "failover": TokenType.FAILOVER,
            "redundant": TokenType.REDUNDANT,
            "clock": TokenType.CLOCK,
            "latency": TokenType.LATENCY,
            "timeout": TokenType.TIMEOUT,
            "window": TokenType.WINDOW,
            "sequence": TokenType.SEQUENCE,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "return": TokenType.RETURN,
            "await": TokenType.AWAIT,
        }

    def current_char(self) -> str | None:
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def peek_char(self, offset: int = 1) -> str | None:
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]

    def advance(self) -> str:
        char = self.current_char()
        self.position += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def skip_whitespace(self):
        while self.current_char() and self.current_char() in " \t\r":
            self.advance()

    def skip_comment(self):
        if self.current_char() == "/" and self.peek_char() == "/":
            while self.current_char() and self.current_char() != "\n":
                self.advance()

    def read_string(self) -> str:
        quote = self.advance()  # Skip opening quote
        value = ""
        while self.current_char() and self.current_char() != quote:
            if self.current_char() == "\\":
                self.advance()
                next_char = self.advance()
                if next_char == "n":
                    value += "\n"
                elif next_char == "t":
                    value += "\t"
                elif next_char == "\\":
                    value += "\\"
                elif next_char == quote:
                    value += quote
                else:
                    value += next_char
            else:
                value += self.advance()
        self.advance()  # Skip closing quote
        return value

    def read_number(self) -> float:
        num_str = ""
        has_dot = False

        while self.current_char() and (self.current_char().isdigit() or self.current_char() == "."):
            if self.current_char() == ".":
                if has_dot:
                    break
                has_dot = True
            num_str += self.advance()

        # Check for scientific notation
        if self.current_char() and self.current_char() in "eE":
            num_str += self.advance()
            if self.current_char() and self.current_char() in "+-":
                num_str += self.advance()
            while self.current_char() and self.current_char().isdigit():
                num_str += self.advance()

        return float(num_str)

    def read_identifier(self) -> str:
        identifier = ""
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == "_"):
            identifier += self.advance()
        return identifier

    def tokenize(self) -> list[Token]:
        self.tokens = []

        while self.position < len(self.source):
            self.skip_whitespace()
            self.skip_comment()

            if self.position >= len(self.source):
                break

            line = self.line
            column = self.column
            char = self.current_char()

            # Newlines
            if char == "\n":
                self.tokens.append(Token(TokenType.NEWLINE, "\\n", line, column))
                self.advance()

            # String literals
            elif char in '"\'':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, line, column))

            # Numbers
            elif char.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, line, column))

            # Identifiers and keywords
            elif char.isalpha() or char == "_":
                identifier = self.read_identifier()
                token_type = self.keywords.get(identifier.lower(), TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, identifier, line, column))

            # Operators and delimiters
            elif char == "(":
                self.tokens.append(Token(TokenType.LPAREN, "(", line, column))
                self.advance()
            elif char == ")":
                self.tokens.append(Token(TokenType.RPAREN, ")", line, column))
                self.advance()
            elif char == "{":
                self.tokens.append(Token(TokenType.LBRACE, "{", line, column))
                self.advance()
            elif char == "}":
                self.tokens.append(Token(TokenType.RBRACE, "}", line, column))
                self.advance()
            elif char == "[":
                self.tokens.append(Token(TokenType.LBRACKET, "[", line, column))
                self.advance()
            elif char == "]":
                self.tokens.append(Token(TokenType.RBRACKET, "]", line, column))
                self.advance()
            elif char == ",":
                self.tokens.append(Token(TokenType.COMMA, ",", line, column))
                self.advance()
            elif char == ";":
                self.tokens.append(Token(TokenType.SEMICOLON, ";", line, column))
                self.advance()
            elif char == ":":
                self.tokens.append(Token(TokenType.COLON, ":", line, column))
                self.advance()
            elif char == ".":
                self.tokens.append(Token(TokenType.DOT, ".", line, column))
                self.advance()
            elif char == "@":
                self.tokens.append(Token(TokenType.AT, "@", line, column))
                self.advance()
            elif char == "#":
                self.tokens.append(Token(TokenType.HASH, "#", line, column))
                self.advance()
            elif char == "$":
                self.tokens.append(Token(TokenType.DOLLAR, "$", line, column))
                self.advance()

            # Multi-character operators
            elif char == "-" and self.peek_char() == ">":
                self.tokens.append(Token(TokenType.ARROW, "->", line, column))
                self.advance()
                self.advance()
            elif char == "=" and self.peek_char() == ">":
                self.tokens.append(Token(TokenType.DOUBLE_ARROW, "=>", line, column))
                self.advance()
                self.advance()
            elif char == "|" and self.peek_char() == ">":
                self.tokens.append(Token(TokenType.PIPE, "|>", line, column))
                self.advance()
                self.advance()
            elif char == "|" and self.peek_char() == "|":
                self.tokens.append(Token(TokenType.PARALLEL, "||", line, column))
                self.advance()
                self.advance()
            elif char == ">" and self.peek_char() == ">":
                self.tokens.append(Token(TokenType.CASCADE, ">>", line, column))
                self.advance()
                self.advance()
            elif char == "=":
                self.tokens.append(Token(TokenType.ASSIGN, "=", line, column))
                self.advance()
            else:
                self.tokens.append(Token(TokenType.OPERATOR, char, line, column))
                self.advance()

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
