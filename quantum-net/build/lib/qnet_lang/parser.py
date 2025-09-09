from qnet_lang.tokens import Tok
from qnet_lang.ast import (
    ProgramNode, NetworkNode, ProtocolNode, NodeDefNode, LinkDefNode, 
    OnNode, SendNode, RecvNode, EntangleNode, ParamNode
)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        statements = []
        while self.current_token() is not None:
            if self.match(Tok.NETWORK):
                statements.append(self.parse_network())
            elif self.match(Tok.PROTOCOL):
                statements.append(self.parse_protocol())
            else:
                raise self.error("Expected 'network' or 'protocol'")
        return ProgramNode(statements)

    def parse_network(self):
        self.expect(Tok.NETWORK)
        name = self.expect(Tok.ID).value
        self.expect(Tok.LBRACE)
        body = self.parse_network_body()
        self.expect(Tok.RBRACE)
        return NetworkNode(name, body)

    def parse_protocol(self):
        self.expect(Tok.PROTOCOL)
        name = self.expect(Tok.ID).value
        self.expect(Tok.LBRACE)
        body = [] # TODO: Parse protocol body
        self.expect(Tok.RBRACE)
        return ProtocolNode(name, body)

    def parse_network_body(self):
        statements = []
        while self.peek() is not None and self.peek().type != Tok.RBRACE:
            current_tok_type = self.peek().type
            if current_tok_type == Tok.NODE:
                 statements.append(self.parse_node_def())
            elif current_tok_type in [Tok.FIBER, Tok.CLASSICAL]:
                statements.append(self.parse_link_def())
            else:
                self.error(f"Unexpected token in network block. Expected NODE, FIBER, or CLASSICAL.")
        return statements

    def parse_node_def(self):
        self.expect(Tok.NODE)
        name = self.expect(Tok.ID).value
        params = self.parse_params()
        self.expect(Tok.SEMI)
        return NodeDefNode(name, params)

    def parse_link_def(self):
        link_type_tok = self.expect_one_of(Tok.FIBER, Tok.CLASSICAL)
        nodes = [self.expect(Tok.ID).value, self.expect(Tok.ID).value]
        params = self.parse_params()
        self.expect(Tok.SEMI)
        return LinkDefNode(link_type_tok.type, nodes, params)

    def parse_params(self):
        params = []
        if self.peek().type == Tok.LPAREN:
            self.expect(Tok.LPAREN)
            while self.peek().type != Tok.RPAREN:
                if self.current_token() is None:
                    self.error("Unclosed parameter list")
                
                param_name = self.expect(Tok.ID).value
                self.expect(Tok.ASSIGN)
                param_value_tok = self.expect_one_of(Tok.ID, Tok.NUM)
                params.append(ParamNode(param_name, param_value_tok.value))
                
                if self.peek().type != Tok.RPAREN:
                    self.expect(Tok.COMMA)
            self.expect(Tok.RPAREN)
        return params

    # --- Helper Methods ---
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1

    def match(self, token_type):
        if self.current_token() and self.current_token().type == token_type:
            self.advance()
            return True
        return False
    
    def expect(self, token_type):
        token = self.current_token()
        if token and token.type == token_type:
            self.advance()
            return token
        self.error(f"Expected {token_type} but got {token.type if token else 'None'}")

    def expect_one_of(self, *token_types):
        token = self.current_token()
        if token and token.type in token_types:
            self.advance()
            return token
        self.error(f"Expected one of {token_types} but got {token.type if token else 'None'}")

    def error(self, message):
        raise Exception(f"Parse Error: {message} at position {self.pos}")
