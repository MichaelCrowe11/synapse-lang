class ASTNode:
    pass

class NetworkNode(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class ProtocolNode(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class NodeDefNode(ASTNode):
    def __init__(self, name, params):
        self.name = name
        self.params = params

class LinkDefNode(ASTNode):
    def __init__(self, link_type, nodes, params):
        self.link_type = link_type
        self.nodes = nodes
        self.params = params

class OnNode(ASTNode):
    def __init__(self, trigger, body):
        self.trigger = trigger
        self.body = body

class SendNode(ASTNode):
    def __init__(self, target, message):
        self.target = target
        self.message = message

class RecvNode(ASTNode):
    def __init__(self, source, action):
        self.source = source
        self.action = action

class EntangleNode(ASTNode):
    def __init__(self, target, params):
        self.target = target
        self.params = params

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class ParamNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value
