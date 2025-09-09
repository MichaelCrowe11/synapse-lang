from enum import Enum, auto
class Tok(Enum):
    NETWORK=auto(); PROTOCOL=auto(); APP=auto(); NODES=auto(); QLINKS=auto(); CLINKS=auto()
    NODE=auto(); FIBER=auto(); CLASSICAL=auto(); ON=auto(); SEND=auto(); RECV=auto()
    ENTANGLE=auto(); USING=auto(); REPEATER=auto(); PURIFICATION=auto(); EXPORT=auto()
    VALIDATE=auto(); RUN=auto(); TRIALS=auto(); REPORT=auto(); USE=auto()
    ID=auto(); NUM=auto(); LBRACE=auto(); RBRACE=auto(); LPAREN=auto(); RPAREN=auto()
    LANGLE=auto(); RANGLE=auto(); COLON=auto(); SEMI=auto(); COMMA=auto(); ASSIGN=auto()
