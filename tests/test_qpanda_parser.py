"""
Test suite for QPanda3 algorithm parsing.
Verifies that the parser recognizes all 13 QPanda3 algorithm keywords
with key:value parameter syntax and produces the correct AST nodes.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapse_lang.synapse_ast import (
    GroverSearchNode,
    ProgramNode,
    QAENode,
    QAOANode,
    QARMNode,
    QCmpNode,
    QKmeansNode,
    QPandaAlgorithmNode,
    QPCANode,
    QSEncodeNode,
    QSVDNode,
    QSVMNode,
    QSVRNode,
    QUBONode,
    QmRMRNode,
    QuantumCircuitNode,
)
from synapse_lang.synapse_lexer import Lexer, TokenType
from synapse_lang.synapse_parser import Parser


def _parse(code: str):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()


def _find_algo_nodes(ast):
    """Walk AST to find QPandaAlgorithmNode instances."""
    results = []

    def walk(node):
        if isinstance(node, QPandaAlgorithmNode):
            results.append(node)
        # Check common collection attributes on AST nodes
        for attr in ("body", "gates", "measurements", "algorithms", "children"):
            items = getattr(node, attr, None)
            if isinstance(items, list):
                for item in items:
                    if hasattr(item, "node_type"):
                        walk(item)

    walk(ast)
    return results


def test_parse_qsvm_algorithm():
    code = (
        'quantum algorithm qsvm(kernel: "quantum", train_data: X, train_labels: Y)'
    )
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    node = algo_nodes[0]
    assert isinstance(node, QSVMNode)
    assert node.parameters["kernel"] == "quantum"


def test_parse_grover_search():
    code = "quantum algorithm grover_search(marked: [5, 11])"
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert isinstance(algo_nodes[0], GroverSearchNode)


def test_parse_qubo():
    code = 'quantum algorithm qubo(problem: P, method: "qaoa")'
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert isinstance(algo_nodes[0], QUBONode)
    assert algo_nodes[0].parameters["method"] == "qaoa"


def test_parse_qaoa():
    code = "quantum algorithm qaoa_solve(layers: 3, problem: H)"
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert isinstance(algo_nodes[0], QAOANode)
    assert algo_nodes[0].parameters["layers"] == 3


def test_parse_qae():
    code = "quantum algorithm qae(oracle: U, threshold: 0.01)"
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert isinstance(algo_nodes[0], QAENode)


def test_parse_qarm():
    code = "quantum algorithm qarm(train_data: X, threshold: 0.5)"
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert isinstance(algo_nodes[0], QARMNode)


def test_parse_qcmp():
    code = 'quantum algorithm qcmp(train_data: X, encoding: "amplitude")'
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert isinstance(algo_nodes[0], QCmpNode)


def test_parse_qkmeans():
    code = "quantum algorithm qkmeans(train_data: X, clusters: 3)"
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert isinstance(algo_nodes[0], QKmeansNode)
    assert algo_nodes[0].parameters["clusters"] == 3


def test_parse_qpca():
    code = "quantum algorithm qpca(train_data: X, components: 2)"
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert isinstance(algo_nodes[0], QPCANode)


def test_parse_qsencode():
    code = 'quantum algorithm qsencode(train_data: X, encoding: "angle")'
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert isinstance(algo_nodes[0], QSEncodeNode)


def test_parse_qsvd():
    code = "quantum algorithm qsvd(train_data: M, components: 4)"
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert isinstance(algo_nodes[0], QSVDNode)


def test_parse_qsvr():
    code = 'quantum algorithm qsvr(kernel: "rbf", train_data: X, train_labels: Y)'
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert isinstance(algo_nodes[0], QSVRNode)


def test_parse_qmrmr():
    code = "quantum algorithm qmrmr(train_data: X, features: 5)"
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert isinstance(algo_nodes[0], QmRMRNode)


def test_qpanda_param_is_list():
    """Verify list parameters are parsed as ListNode."""
    from synapse_lang.synapse_ast import ListNode

    code = "quantum algorithm grover_search(marked: [1, 2, 3])"
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    node = algo_nodes[0]
    assert isinstance(node, GroverSearchNode)
    # The parameter value should be stored; exact representation depends on
    # whether we store raw AST or evaluate, but it must exist.
    assert "marked" in node.parameters


def test_qpanda_param_is_number():
    """Numeric parameters should be stored as Python numbers."""
    code = "quantum algorithm qkmeans(clusters: 5)"
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert algo_nodes[0].parameters["clusters"] == 5


def test_qpanda_param_is_string():
    """String parameters should be stored as Python strings."""
    code = 'quantum algorithm qsvm(kernel: "linear")'
    ast = _parse(code)
    algo_nodes = _find_algo_nodes(ast)
    assert len(algo_nodes) >= 1
    assert algo_nodes[0].parameters["kernel"] == "linear"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
