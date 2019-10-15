import pytest
from blockchain import *


def test_initialization():
    # Create the first node in the network
    node_a = Node(initial_coins=200)

    # When a node is created, it should create an initial transaction, giving itself the initial amount of coins
    assert len(node_a._signed_transactions) == 1

    # The object added should be a SignedTransaction (the signature can be a stub, like "signed")
    assert isinstance(node_a._signed_transactions[0], SignedTransaction)

    # Verify the transaction was created correctly
    assert node_a._signed_transactions[0].transaction.coins == 200
    assert node_a._signed_transactions[0].transaction.to_address == node_a.address

    # The transaction didn't come from anyone specific, it's just a way to initialize the network
    assert node_a._signed_transactions[0].transaction.from_address != node_a.address

    # The first node doesn't know about any other nodes
    assert node_a._other_nodes == []


def test_balance_after_initialization():
    node_a = Node(initial_coins=200)

    # calculate_balance for a single transaction
    assert node_a.calculate_balance(node_a.address) == 200


def test_second_node_initialization():
    node_a = Node(initial_coins=200)

    node_b = Node(other_nodes=[node_a])

    # The new node should know about the existing nodes
    assert node_b._other_nodes == [node_a]

def test_make_transaction_updates_transactions():
    node_a = Node(initial_coins=200)

    node_b = Node(other_nodes=[node_a])

    node_a.transfer_coins(node_b.address, coins=50)

    # transfer_coins created a new transaction
    assert len(node_a._signed_transactions) == 2

    # The 1st transaction is still correct
    assert node_a._signed_transactions[0].transaction.coins == 200
    assert node_a._signed_transactions[0].transaction.to_address == node_a.address

    # The 2nd transaction is correct
    assert node_a._signed_transactions[1].transaction.coins == 50
    assert node_a._signed_transactions[1].transaction.to_address == node_b.address
    assert node_a._signed_transactions[1].transaction.from_address == node_a.address


def test_balance():
    node_a = Node(initial_coins=200)
    node_b = Node(other_nodes=[node_a])
    node_a.transfer_coins(node_b.address, coins=50)

    # Node A knows the balances
    assert node_a.calculate_balance(node_a.address) == 150
    assert node_a.calculate_balance(node_b.address) == 50


# Unguided mode: You may ignore all other tests and skip directly to this one
def test_balance_after_transaction():
    node_a = Node(initial_coins=200)
    node_b = Node(other_nodes=[node_a])

    node_a.transfer_coins(node_b.address, coins=50)

    # Node A knows the balances
    assert node_a.calculate_balance(node_a.address) == 150
    assert node_a.calculate_balance(node_b.address) == 50


#@pytest.mark.skip(reason="Bonus")
def test_sync_transactions_between_nodes():
    node_a = Node(initial_coins=200)
    node_b = Node(other_nodes=[node_a])

    node_a.transfer_coins(node_b.address, coins=50)

    # Node A knows the balances
    assert node_a.calculate_balance(node_a.address) == 150
    assert node_a.calculate_balance(node_b.address) == 50

    node_b.pull_transactions_from_other_nodes()

    # Node B knows the balances
    assert node_b.calculate_balance(node_a.address) == 150
    assert node_b.calculate_balance(node_b.address) == 50

def test_signature():
    node_a = Node(initial_coins=200)
    node_b = Node(other_nodes=[node_a])
    node_a.transfer_coins(node_b.address, coins=50)

    signed_transaction = node_a._signed_transactions[1]

    assert Node.is_signed_transaction_valid(signed_transaction)