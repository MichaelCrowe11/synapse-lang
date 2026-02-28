from synapse_lang.synapse_lexer import Lexer, TokenType


def test_algorithm_keyword_tokens_exist():
    expected = [
        "GROVER_SEARCH", "QAOA_SOLVE", "QAE", "QARM", "QCMP",
        "QKMEANS", "QPCA", "QSENCODE", "QSVD", "QSVM", "QSVR",
        "QUBO", "QMRMR",
    ]
    for name in expected:
        assert hasattr(TokenType, name), f"TokenType.{name} missing"


def test_parameter_keyword_tokens_exist():
    expected = [
        "QPANDA3", "TRAIN_DATA", "TRAIN_LABELS", "TEST_DATA",
        "CLUSTERS", "FEATURES", "ORACLE_KW", "THRESHOLD",
        "LAYERS", "COMPONENTS", "ENCODING", "MARKED",
    ]
    for name in expected:
        assert hasattr(TokenType, name), f"TokenType.{name} missing"


def test_lexer_tokenizes_algorithm_keyword():
    lexer = Lexer("algorithm qsvm()")
    tokens = lexer.tokenize()
    token_types = [t.type for t in tokens if t.type != TokenType.EOF]
    assert TokenType.ALGORITHM in token_types
    assert TokenType.QSVM in token_types


def test_lexer_tokenizes_grover():
    lexer = Lexer("algorithm grover_search(marked: [5])")
    tokens = lexer.tokenize()
    token_types = [t.type for t in tokens if t.type != TokenType.EOF]
    assert TokenType.GROVER_SEARCH in token_types
    assert TokenType.MARKED in token_types
