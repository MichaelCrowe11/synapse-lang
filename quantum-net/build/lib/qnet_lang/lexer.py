from qnet_lang.tokens import Tok
import re

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = []
        self.keywords = {
            'network': Tok.NETWORK,
            'protocol': Tok.PROTOCOL,
            'app': Tok.APP,
            'nodes': Tok.NODES,
            'qlinks': Tok.QLINKS,
            'clinks': Tok.CLINKS,
            'node': Tok.NODE,
            'fiber': Tok.FIBER,
            'classical': Tok.CLASSICAL,
            'on': Tok.ON,
            'send': Tok.SEND,
            'recv': Tok.RECV,
            'entangle': Tok.ENTANGLE,
            'using': Tok.USING,
            'repeater': Tok.REPEATER,
            'purification': Tok.PURIFICATION,
            'export': Tok.EXPORT,
            'validate': Tok.VALIDATE,
            'run': Tok.RUN,
            'trials': Tok.TRIALS,
            'report': Tok.REPORT,
            'use': Tok.USE,
        }
        self.token_specs = [
            ('SKIP',       r'[ \t\r\n]+'),
            ('COMMENT',    r'#.*'),
            ('NUM',        r'\d+(\.\d*)?'),
            ('ID',         r'[A-Za-z_][A-Za-z0-9_]*'),
            ('LBRACE',     r'\{'),
            ('RBRACE',     r'\}'),
            ('LPAREN',     r'\('),
            ('RPAREN',     r'\)'),
            ('LANGLE',     r'<'),
            ('RANGLE',     r'>'),
            ('COLON',      r':'),
            ('SEMI',       r';'),
            ('COMMA',      r','),
            ('ASSIGN',     r'='),
            ('MISMATCH',   r'.'),
        ]
        self.token_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_specs)

    def lex(self):
        for mo in re.finditer(self.token_regex, self.text):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP' or kind == 'COMMENT':
                continue
            elif kind == 'ID':
                kind = self.keywords.get(value.lower(), Tok.ID)
                self.tokens.append((kind, value))
            elif kind == 'NUM':
                self.tokens.append((Tok.NUM, float(value) if '.' in value else int(value)))
            elif kind != 'MISMATCH':
                self.tokens.append((Tok[kind], value))
            else:
                raise RuntimeError(f'Unexpected character: {value}')
        return self.tokens

def tokenize(text):
    lexer = Lexer(text)
    return lexer.lex()
