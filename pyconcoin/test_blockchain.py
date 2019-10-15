from blockchain import *

A_ADDRESS = "NODE_A_ADDRESS"
B_ADDRESS = "NODE_B_ADDRESS"


# This is not a test, it helps shorten one of the tests
def create_block(previous_block, from_address: Optional[str] = A_ADDRESS, to_address=B_ADDRESS, coins=10):
    signed_transaction = SignedTransaction(Transaction(from_address=from_address,
                                                       to_address=to_address,
                                                       coins=coins),
                                           signature="signed")
    return Block(signed_transaction=signed_transaction,
                 magic_number=random.randint(0, 99),
                 previous_block=previous_block)


def test_init_address():
    node_a = Node(coins=200)
    assert node_a.address is not None  # Give me some random address


def test_init_starter_block():
    node_a = Node(coins=200)

    # When creating the first node, an initial block should be created.
    # This block should give this new node some initial coins
    assert node_a.get_blockchain() is not None  # One block should exist after creating the first node
    assert node_a.get_blockchain().previous_block is None
    assert node_a.get_blockchain().signed_transaction.transaction.coins == 200
    assert node_a.get_blockchain().signed_transaction.transaction.to_address == node_a.address


def test_get_blockchain():
    node_a = Node(coins=200)

    # The getter should just return the _last_block
    assert node_a.get_blockchain() == node_a._last_block


def test_get_balance_without_node():
    # Unit tests for get_balance: Block creation
    block_1 = create_block(previous_block=None, from_address=None, to_address=A_ADDRESS, coins=100)

    # One block exists, with a transaction giving Node A 100 coins. So calculate_balance should return 100
    assert Node.calculate_balance(A_ADDRESS, block_1) == 100

    # If Node A pays, they Node A should have less coins
    block_2 = create_block(previous_block=block_1, from_address=A_ADDRESS, to_address=B_ADDRESS, coins=10)
    assert Node.calculate_balance(A_ADDRESS, block_2) == 90
    block_3 = create_block(previous_block=block_2, from_address=A_ADDRESS, to_address=B_ADDRESS, coins=10)
    assert Node.calculate_balance(A_ADDRESS, block_3) == 80
    block_4 = create_block(previous_block=block_3, from_address=A_ADDRESS, to_address=B_ADDRESS, coins=10)
    assert Node.calculate_balance(A_ADDRESS, block_4) == 70

    # If Node B gets coins, then Node B should have more coins
    assert Node.calculate_balance(B_ADDRESS, block_1) == 0  # Node B doesn't exist in block_1 (see the creation above)
    assert Node.calculate_balance(B_ADDRESS, block_2) == 10
    assert Node.calculate_balance(B_ADDRESS, block_3) == 20
    assert Node.calculate_balance(B_ADDRESS, block_4) == 30


def test_node_get_balance():
    node_a = Node(coins=200)

    # Make sure Node A can calculate the balance from the block
    assert Node.calculate_balance(node_a.address, node_a.get_blockchain()) == 200


def test_initialize_second_node():
    node_a = Node(coins=200)
    node_b = Node(other_nodes=[node_a])

    # Give me some random address
    assert node_b.address is not None

    # (Hopefully my address is different from A's address. Otherwise, try running the test again)
    assert node_b.address != node_a.address

    # Initialize a new node's blockchain with a blockchain from an existing node
    assert node_b.get_blockchain() == node_a.get_blockchain()

    # Save the "other_nodes" sent in the constructor
    assert node_b._other_nodes == [node_a]


def test_first_node_knows_all_balances_after_initialization():
    node_a = Node(coins=200)
    node_b = Node(other_nodes=[node_a])

    # Node A should know the balances
    assert Node.calculate_balance(node_a.address, node_a.get_blockchain()) == 200
    assert Node.calculate_balance(node_b.address, node_a.get_blockchain()) == 0


def test_new_node_knows_all_balances_after_initialization():
    node_a = Node(coins=200)
    node_b = Node(other_nodes=[node_a])

    # Node B should know the balances
    assert Node.calculate_balance(node_a.address, node_b.get_blockchain()) == 200
    assert Node.calculate_balance(node_b.address, node_b.get_blockchain()) == 0


def test_transfer_coins_creates_new_block():
    node_a = Node(coins=200)
    node_b = Node(other_nodes=[node_a])

    last_block_before_transfer = node_a.get_blockchain()

    node_a.transfer_coins(to_address=node_b.address, coins=50)

    last_block_after_transfer = node_a.get_blockchain()

    # transfer_coins should create a new block (with the new transaction) pointing at the previously last block
    assert last_block_after_transfer.previous_block == last_block_before_transfer

    # The transaction of the newly added block should have sent 50 coins
    assert last_block_after_transfer.signed_transaction.transaction.coins == 50

def test_sender_knows_new_balances():
    node_a = Node(coins=200)
    node_b = Node(other_nodes=[node_a])

    node_a.transfer_coins(to_address=node_b.address, coins=50)

    assert Node.calculate_balance(node_a.address, node_a.get_blockchain()) == 150
    assert Node.calculate_balance(node_b.address, node_a.get_blockchain()) == 50


def test_receiver_knows_updated_blockchain_after_pull_blockchains():
    node_a = Node(coins=200)
    node_b = Node(other_nodes=[node_a])

    node_a.transfer_coins(to_address=node_b.address, coins=50)

    # B asks A what history A knows about
    node_b.pull_blockchains_from_other_nodes()

    # B should know about A's blockchain
    assert node_b.get_blockchain() == node_a.get_blockchain()


def test_receiver_knows_balance_after_pull_blockchains():
    node_a = Node(coins=200)
    node_b = Node(other_nodes=[node_a])

    node_a.transfer_coins(to_address=node_b.address, coins=50)

    # B doesn't know about the transfer yet
    # Did this test fail?
    # If B already knows that the balances are 150, 50: That's ok, you can comment out these two lines and continue
    assert Node.calculate_balance(node_a.address, node_b.get_blockchain()) == 200
    assert Node.calculate_balance(node_b.address, node_b.get_blockchain()) == 0

    # B asks A what history A knows about
    node_b.pull_blockchains_from_other_nodes()

    # Make sure Node B knows the balances, after pull_blockchains
    assert Node.calculate_balance(node_a.address, node_b.get_blockchain()) == 150
    assert Node.calculate_balance(node_b.address, node_b.get_blockchain()) == 50


# Make sure the previous capabilities still exist, since we refactored things
def test_balance_after_transaction():
    node_a = Node(coins=200)
    node_b = Node(other_nodes=[node_a])
    node_a.transfer_coins(node_b.address, coins=50)

    # Node A knows the balances
    assert Node.calculate_balance(node_a.address, node_a.get_blockchain()) == 150
    assert Node.calculate_balance(node_b.address, node_a.get_blockchain()) == 50


def test_merge_blockchains__one_is_longer__picks_longer_one():
    # A --> B1
    # A --> B2 --> C2
    block_a = create_block(previous_block=None)
    block_b1 = create_block(previous_block=block_a)
    block_b2 = create_block(previous_block=block_a)
    block_c2 = create_block(previous_block=block_b2)
    assert block_a == block_a
    assert block_b1 != block_b2
    assert Node.merge_blockchains(block_a, block_a) == block_a
    assert Node.merge_blockchains(block_b1, block_b1) == block_b1
    assert Node.merge_blockchains(block_c2, block_b1) == block_c2
    assert Node.merge_blockchains(block_b1, block_c2) == block_c2