# import pytest
import os
import sys
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dataplug


"""
    Use database parameters:
        - port 7144
        - no authentication

"""


def test_check_mandatory_fields():
    node_a = dataplug.Node(data={"A": 3.4}, mandatory_features=["B", "C"])
    data = {"B": 2.3, "D": 0.0}
    for field in ["A", "B", "C"]:
        assert field in node_a.data
    assert "D" not in node_a.data

    node_a.data = data
    for field in ["B", "C", "D"]:
        assert field in node_a.data
    assert "A" not in node_a.data


def test_full_key():
    C8 = "node_test"
    client_config = {"protocol": "http", "port": 7144}

    node_a = dataplug.Node(data={"A": 3.4, "_key": "albert"},
                           client_config=client_config,
                           mandatory_features=["B", "C"])
    node_a.client.collection = C8
    assert node_a.key() == "albert"
    assert node_a.full_key() == C8+"/albert"

    node_a.client.delete_collection()


def test_filter_node_data():
    D1 = "dataflexT7"
    C1 = "fip"
    client_config = {"protocol": "http", "port": 7144}

    node_a = dataplug.Node(D1, C1, data={"A": 3.4, "_key": "albert"},
                           client_config=client_config,
                           mandatory_features=["B", "C"])
    assert node_a.client.is_connected() is True
    node_data = node_a.filter_data()
    assert "_key" not in node_data
    assert "_rev" not in node_data
    assert "_id" not in node_data
    assert "A" in node_data
    assert "B" in node_data
    assert "C" in node_data

    node_data = node_a.filter_data(keep_fields=["_key"])
    assert "_key" in node_data
    assert "_rev" not in node_data
    assert "_id" not in node_data
    assert "A" in node_data
    assert "B" in node_data
    assert "C" in node_data

    node_a.client.delete_collection()


def test_node_upsave():
    client_config = {"protocol": "http", "port": 7144}

    node_nokey1 = dataplug.Node(
                           data={"A": 1.41},
                           client_config=client_config,
                           mandatory_features=["A", "B", "C"])
    node_nokey2 = dataplug.Node(
                           data={"A": 1.41, "more": "is_less"},
                           client_config=client_config,
                           mandatory_features=["A", "B", "C"])
    node_nokey3 = dataplug.Node(
                           data={"A": 1.41, "tiny": "angstrom"},
                           client_config=client_config,
                           mandatory_features=["A", "B", "C"])
    node_key = dataplug.Node(
                           data={"A": 3.14, "_key": "einstein"},
                           client_config=client_config,
                           mandatory_features=["A", "B", "C"])

    assert node_nokey1.key() == ""
    assert node_nokey2.key() == ""
    assert node_nokey3.key() == ""
    assert node_key.key() == "einstein"

    assert node_key.upsave() is True
    assert node_key.key() == "einstein"

    assert node_nokey1.upsave() is True
    assert len(node_nokey1.key()) > 0
    assert "more" not in node_nokey1.data
    assert "tiny" not in node_nokey1.data

    assert node_nokey2.upsave(update=True) is True
    assert node_nokey2.key() == node_nokey1.key()
    assert "more" not in node_nokey1.data
    assert "more" in node_nokey2.data
    assert "tiny" not in node_nokey2.data

    assert node_nokey3.upsave() is True
    assert node_nokey3.key() != node_nokey1.key()
    assert node_nokey3.key() != node_nokey2.key()
    assert "more" not in node_nokey3.data
    assert "tiny" in node_nokey3.data

    # client.delete_collection()
