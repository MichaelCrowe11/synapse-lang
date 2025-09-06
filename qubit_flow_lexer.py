# Qubit-Flow Quantum Computing Language - Lexer
# Complementary to Synapse-Lang for pure quantum computation

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Iterator

class TokenType(Enum):
    # Quantum-specific keywords
    QUBIT = auto()
    QUDIT = auto()
    CIRCUIT = auto()
    GATE = auto()
    MEASURE = auto()
    ENTANGLE = auto()
    SUPERPOSE = auto()
    TELEPORT = auto()
    
    # Quantum gates
    H = auto()          # Hadamard
    X = auto()          # Pauli-X
    Y = auto()          # Pauli-Y  
    Z = auto()          # Pauli-Z
    CNOT = auto()       # Controlled-NOT
    CZ = auto()         # Controlled-Z
    RX = auto()         # Rotation-X
    RY = auto()         # Rotation-Y
    RZ = auto()         # Rotation-Z
    PHASE = auto()      # Phase gate
    TOFFOLI = auto()    # Toffoli gate
    
    # Quantum algorithms
    GROVERS = auto()
    SHORS = auto()
    VQE = auto()
    QAOA = auto()
    QFT = auto()        # Quantum Fourier Transform
    
    # Error correction
    SYNDROME = auto()
    CORRECT = auto()
    STABILIZER = auto()
    
    # Classical control
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    
    # Operators
    TENSOR = auto()     # ⊗
    DAGGER = auto()     # †
    AMPLITUDE = auto()  # |ψ⟩
    BRAKET = auto()     # ⟨φ|ψ⟩
    
    # Basic tokens
    IDENTIFIER = auto()
    NUMBER = auto()
    COMPLEX = auto()
    STRING = auto()
    
    # Delimiters
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACKET = auto()   # [
    RBRACKET = auto()   # ]
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    
    # Quantum state notation
    KET = auto()        # |
    BRA = auto()        # ⟨
    
    # Punctuation
    SEMICOLON = auto()  # ;
    COMMA = auto()      # ,
    DOT = auto()        # .
    ARROW = auto()      # ->
    ASSIGN = auto()     # =
    
    # Newlines and end
    NEWLINE = auto()
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class QubitFlowLexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        
        # Quantum-specific keywords
        self.keywords = {
            'qubit': TokenType.QUBIT,
            'qudit': TokenType.QUDIT,
            'circuit': TokenType.CIRCUIT,
            'gate': TokenType.GATE,
            'measure': TokenType.MEASURE,
            'entangle': TokenType.ENTANGLE,
            'superpose': TokenType.SUPERPOSE,
            'teleport': TokenType.TELEPORT,
            
            # Quantum gates
            'H': TokenType.H,
            'X': TokenType.X,
            'Y': TokenType.Y,
            'Z': TokenType.Z,
            'CNOT': TokenType.CNOT,
            'CZ': TokenType.CZ,
            'RX': TokenType.RX,
            'RY': TokenType.RY,
            'RZ': TokenType.RZ,
            'PHASE': TokenType.PHASE,
            'TOFFOLI': TokenType.TOFFOLI,
            
            # Quantum algorithms
            'grovers': TokenType.GROVERS,
            'shors': TokenType.SHORS,
            'vqe': TokenType.VQE,
            'qaoa': TokenType.QAOA,
            'qft': TokenType.QFT,
            
            # Error correction
            'syndrome': TokenType.SYNDROME,
            'correct': TokenType.CORRECT,
            'stabilizer': TokenType.STABILIZER,
            
            # Classical control
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
        }
        
    def current_char(self) -> Optional[str]:
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        peek_pos = self.position + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self):
        if self.position < len(self.source):
            if self.current_char() == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self) -> Token:
        start_line = self.line
        start_col = self.column
        num_str = ''
        
        # Handle complex numbers (e.g., 1+2i, 0.5-0.3i)
        has_imaginary = False
        
        while (self.current_char() and 
               (self.current_char().isdigit() or 
                self.current_char() in '.+-i')):
            if self.current_char() == 'i':
                has_imaginary = True
            num_str += self.current_char()
            self.advance()
        
        token_type = TokenType.COMPLEX if has_imaginary else TokenType.NUMBER
        return Token(token_type, num_str, start_line, start_col)
    
    def read_identifier(self) -> Token:
        start_line = self.line
        start_col = self.column
        identifier = ''
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() == '_')):
            identifier += self.current_char()
            self.advance()
        
        # Check if it's a keyword
        token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
        return Token(token_type, identifier, start_line, start_col)
    
    def read_string(self) -> Token:
        start_line = self.line
        start_col = self.column
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        
        string_value = ''
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char():
                    string_value += self.current_char()
                    self.advance()
            else:
                string_value += self.current_char()
                self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote
        
        return Token(TokenType.STRING, string_value, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        tokens = []
        
        while self.position < len(self.source):
            self.skip_whitespace()
            
            if not self.current_char():
                break
                
            char = self.current_char()
            start_line = self.line
            start_col = self.column
            
            # Comments
            if char == '#':
                self.skip_comment()
                continue
            
            # Newlines
            if char == '\n':
                tokens.append(Token(TokenType.NEWLINE, char, start_line, start_col))
                self.advance()
                continue
            
            # Numbers (including complex)
            if char.isdigit() or char == '.':
                tokens.append(self.read_number())
                continue
            
            # Identifiers and keywords
            if char.isalpha() or char == '_':
                tokens.append(self.read_identifier())
                continue
            
            # Strings
            if char in '"\'':
                tokens.append(self.read_string())
                continue
            
            # Special quantum notation
            if char == '|':
                tokens.append(Token(TokenType.KET, char, start_line, start_col))
                self.advance()
                continue
                
            if char == '⟨':
                tokens.append(Token(TokenType.BRA, char, start_line, start_col))
                self.advance()
                continue
            
            if char == '⊗':
                tokens.append(Token(TokenType.TENSOR, char, start_line, start_col))
                self.advance()
                continue
                
            if char == '†':
                tokens.append(Token(TokenType.DAGGER, char, start_line, start_col))
                self.advance()
                continue
            
            # Multi-character operators
            if char == '-' and self.peek_char() == '>':
                tokens.append(Token(TokenType.ARROW, '->', start_line, start_col))
                self.advance()
                self.advance()
                continue
            
            # Single-character tokens
            single_chars = {
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA,
                '.': TokenType.DOT,
                '=': TokenType.ASSIGN,
            }
            
            if char in single_chars:
                tokens.append(Token(single_chars[char], char, start_line, start_col))
                self.advance()
                continue
            
            # Unknown character - skip it
            self.advance()
        
        tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return tokens