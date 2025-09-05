import re
import ast
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import defaultdict

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
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self) -> float:
        start = self.position
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break
                has_dot = True
            self.advance()
        
        return float(self.source[start:self.position])
    
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
                self.tokens.append(Token(TokenType.NEWLINE, "\\n", line, column))
            
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
                identifier = self.read_identifier()
                token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, identifier, line, column))
            
            else:
                self.advance()  # Skip unknown characters
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

@dataclass
class UncertainValue:
    value: float
    uncertainty: float
    
    def __repr__(self):
        return f"{self.value} ± {self.uncertainty}"
    
    def __add__(self, other):
        if isinstance(other, UncertainValue):
            return UncertainValue(
                self.value + other.value,
                (self.uncertainty**2 + other.uncertainty**2)**0.5
            )
        return UncertainValue(self.value + other, self.uncertainty)
    
    def __mul__(self, other):
        if isinstance(other, UncertainValue):
            return UncertainValue(
                self.value * other.value,
                self.value * other.value * ((self.uncertainty/self.value)**2 + 
                                           (other.uncertainty/other.value)**2)**0.5
            )
        return UncertainValue(self.value * other, abs(self.uncertainty * other))

class ParallelStream:
    def __init__(self, name: str, function):
        self.name = name
        self.function = function
        self.result = None
        self.lock = threading.Lock()
    
    def execute(self):
        self.result = self.function()
        return self.result

class SynapseInterpreter:
    def __init__(self):
        self.variables = {}
        self.hypotheses = {}
        self.experiments = {}
        self.streams = {}
        self.executor = ThreadPoolExecutor(max_workers=8)
        
    def execute(self, source: str):
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        return self.parse_and_execute(tokens)
    
    def parse_and_execute(self, tokens: List[Token]):
        results = []
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == TokenType.EOF:
                break
            
            if token.type == TokenType.NEWLINE:
                i += 1
                continue
            
            if token.type == TokenType.PARALLEL:
                result = self.execute_parallel_block(tokens, i)
                results.append(result)
                i = self.find_block_end(tokens, i) + 1
                
            elif token.type == TokenType.UNCERTAIN:
                result = self.parse_uncertain_value(tokens, i)
                results.append(result)
                while tokens[i].type != TokenType.NEWLINE and tokens[i].type != TokenType.EOF:
                    i += 1
                    
            elif token.type == TokenType.IDENTIFIER:
                if i + 1 < len(tokens) and tokens[i + 1].type == TokenType.ASSIGN:
                    var_name = token.value
                    i += 2  # Skip identifier and =
                    value = self.parse_expression(tokens, i)
                    self.variables[var_name] = value
                    results.append(f"{var_name} = {value}")
                    while tokens[i].type != TokenType.NEWLINE and tokens[i].type != TokenType.EOF:
                        i += 1
                else:
                    i += 1
            else:
                i += 1
        
        return results
    
    def execute_parallel_block(self, tokens: List[Token], start_idx: int):
        i = start_idx + 1
        
        while tokens[i].type != TokenType.LEFT_BRACE:
            i += 1
        i += 1  # Skip {
        
        branches = []
        
        while tokens[i].type != TokenType.RIGHT_BRACE:
            if tokens[i].type == TokenType.BRANCH:
                i += 1
                branch_name = tokens[i].value
                i += 2  # Skip name and :
                
                # Simple expression parsing for demo
                expr_start = i
                while tokens[i].type != TokenType.NEWLINE and tokens[i].type != TokenType.RIGHT_BRACE:
                    i += 1
                
                branches.append((branch_name, lambda: f"Executed branch {branch_name}"))
            
            if tokens[i].type == TokenType.NEWLINE:
                i += 1
            elif tokens[i].type != TokenType.RIGHT_BRACE:
                i += 1
        
        # Execute branches in parallel
        futures = []
        for branch_name, branch_func in branches:
            future = self.executor.submit(branch_func)
            futures.append((branch_name, future))
        
        results = {}
        for branch_name, future in futures:
            results[branch_name] = future.result()
        
        return {"parallel_execution": results}
    
    def parse_uncertain_value(self, tokens: List[Token], start_idx: int):
        i = start_idx + 1
        
        while tokens[i].type != TokenType.IDENTIFIER:
            i += 1
        
        var_name = tokens[i].value
        i += 1
        
        while tokens[i].type != TokenType.NUMBER:
            i += 1
        
        value = tokens[i].value
        i += 1
        
        if i < len(tokens) and tokens[i].type == TokenType.UNCERTAINTY:
            i += 1
            uncertainty = tokens[i].value
            uncertain_val = UncertainValue(value, uncertainty)
            self.variables[var_name] = uncertain_val
            return f"{var_name} = {uncertain_val}"
        
        return f"{var_name} = {value}"
    
    def parse_expression(self, tokens: List[Token], start_idx: int):
        # Simplified expression parsing
        i = start_idx
        
        if tokens[i].type == TokenType.NUMBER:
            return tokens[i].value
        elif tokens[i].type == TokenType.STRING:
            return tokens[i].value
        elif tokens[i].type == TokenType.IDENTIFIER:
            return self.variables.get(tokens[i].value, tokens[i].value)
        
        return None
    
    def find_block_end(self, tokens: List[Token], start_idx: int):
        i = start_idx
        brace_count = 0
        
        while i < len(tokens):
            if tokens[i].type == TokenType.LEFT_BRACE:
                brace_count += 1
            elif tokens[i].type == TokenType.RIGHT_BRACE:
                brace_count -= 1
                if brace_count == 0:
                    return i
            i += 1
        
        return len(tokens) - 1

def main():
    interpreter = SynapseInterpreter()
    
    # Example 1: Uncertain values
    code1 = """
    uncertain measurement = 42.3 ± 0.5
    uncertain temperature = 300 ± 10
    """
    
    print("Example 1: Uncertain Values")
    print("-" * 40)
    results = interpreter.execute(code1)
    for result in results:
        print(result)
    
    # Example 2: Parallel execution
    code2 = """
    parallel {
        branch A: test_condition_1
        branch B: test_condition_2
        branch C: test_condition_3
    }
    """
    
    print("\nExample 2: Parallel Execution")
    print("-" * 40)
    results = interpreter.execute(code2)
    for result in results:
        print(result)
    
    # Example 3: Variable assignment
    code3 = """
    x = 10
    y = 20
    name = "Synapse"
    """
    
    print("\nExample 3: Variable Assignment")
    print("-" * 40)
    results = interpreter.execute(code3)
    for result in results:
        print(result)

if __name__ == "__main__":
    main()