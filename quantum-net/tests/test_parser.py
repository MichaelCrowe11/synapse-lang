import unittest
from qnet_lang.lexer import Lexer
from qnet_lang.parser import Parser
from qnet_lang.ast import ProgramNode, NetworkNode, NodeDefNode, LinkDefNode, ParamNode
from qnet_lang.tokens import Tok

class TestParser(unittest.TestCase):

    def test_parse_network(self):
        code = """
        network teleport_network {
            node alice;
            node bob;
            node charlie;
            fiber(length=10) alice bob;
            classical(delay=5) alice bob;
        }
        """
        lexer = Lexer(code)
        tokens = lexer.lex()
        
        # We need to filter out the token objects and just pass the types for now
        # This is a temporary fix until the parser is more robust
        # token_tuples = [(t.type, t.value) for t in tokens]

        parser = Parser(tokens)
        ast = parser.parse()

        self.assertIsInstance(ast, ProgramNode)
        self.assertEqual(len(ast.statements), 1)

        network = ast.statements[0]
        self.assertIsInstance(network, NetworkNode)
        self.assertEqual(network.name, "teleport_network")

        # Check node definitions
        self.assertIsInstance(network.body[0], NodeDefNode)
        self.assertEqual(network.body[0].name, "alice")
        self.assertEqual(len(network.body[0].params), 0)

        self.assertIsInstance(network.body[1], NodeDefNode)
        self.assertEqual(network.body[1].name, "bob")

        self.assertIsInstance(network.body[2], NodeDefNode)
        self.assertEqual(network.body[2].name, "charlie")

        # Check link definitions
        fiber_link = network.body[3]
        self.assertIsInstance(fiber_link, LinkDefNode)
        self.assertEqual(fiber_link.link_type, Tok.FIBER)
        self.assertEqual(fiber_link.nodes, ["alice", "bob"])
        self.assertEqual(len(fiber_link.params), 1)
        self.assertEqual(fiber_link.params[0].name, "length")
        self.assertEqual(fiber_link.params[0].value, 10)

        classical_link = network.body[4]
        self.assertIsInstance(classical_link, LinkDefNode)
        self.assertEqual(classical_link.link_type, Tok.CLASSICAL)
        self.assertEqual(classical_link.nodes, ["alice", "bob"])
        self.assertEqual(len(classical_link.params), 1)
        self.assertEqual(classical_link.params[0].name, "delay")
        self.assertEqual(classical_link.params[0].value, 5)

if __name__ == '__main__':
    unittest.main()
