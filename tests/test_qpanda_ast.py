from synapse_lang.synapse_ast import (
    QPandaAlgorithmNode,
    GroverSearchNode,
    QSVMNode,
    QPCANode,
    QAOANode,
    QAENode,
    QARMNode,
    QCmpNode,
    QKmeansNode,
    QSEncodeNode,
    QSVDNode,
    QSVRNode,
    QUBONode,
    QmRMRNode,
)


def test_base_node_has_name_and_params():
    node = QPandaAlgorithmNode(name="qsvm", parameters={"kernel": "quantum"})
    assert node.name == "qsvm"
    assert node.parameters["kernel"] == "quantum"


def test_qsvm_node():
    node = QSVMNode(
        parameters={"train_data": "X", "train_labels": "Y", "kernel": "quantum"}
    )
    assert node.name == "qsvm"
    assert "train_data" in node.parameters


def test_grover_node():
    node = GroverSearchNode(parameters={"marked": [5, 11], "iterations": "auto"})
    assert node.name == "grover_search"


def test_all_13_node_classes_exist():
    classes = [
        GroverSearchNode, QAOANode, QAENode, QARMNode,
        QCmpNode, QKmeansNode, QPCANode, QSEncodeNode,
        QSVDNode, QSVMNode, QSVRNode, QUBONode, QmRMRNode,
    ]
    for cls in classes:
        node = cls(parameters={})
        assert isinstance(node, QPandaAlgorithmNode)
        assert isinstance(node.name, str)
