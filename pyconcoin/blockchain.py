import random
from dataclasses import dataclass
from typing import List, Optional
import time
import hashlib


@dataclass
class Transaction:
    from_address: Optional[str]  # In the first transaction, from_address will be None
    to_address: str
    coins: int


@dataclass
class SignedTransaction:
    transaction: Transaction
    signature: str


@dataclass
class Block:  # HistoryState
    signed_transaction: SignedTransaction
    previous_block: Optional['Block']  # In the first block, previous_block will be None
    magic_number: int


class Node:
    def __init__(self, other_nodes: List['Node'] = None, coins: int = None):
        self.address = random.randint(0, 1000)
        self._other_nodes: List['Node'] = []
        self._last_block: Optional[Block] = None

        # If I'm the first node
        if other_nodes is None and coins is not None:
            initial_transaction = Transaction(from_address=None, to_address=self.address, coins=coins)
            initial_signed_transaction = self.sign(initial_transaction)

            # TODO: Create an initial block and save it as the _last_block. Hint: Use create_block
            self._last_block = self.create_block(initial_signed_transaction, None)
            pass

        # If I'm not the first node
        elif other_nodes is not None and coins is None:
            self._other_nodes = other_nodes

            # TODO: Give self._last_block a default value: Set it to the blockchain of one of the other nodes
            self._last_block = other_nodes[0]._last_block
            pass

        else:
            raise Exception("")

    def get_blockchain(self) -> Block:
        # TODO: Return the blockchain I know about.
        # Hint: The blockchain is a linked list, so returning the last block is enough,
        # because it points at all the previous blocks
        return self._last_block

    def create_block(self, signed_transaction, previous_block) -> Block:
        # As a stub implementation, just use magic_number=0, and sleep a bit
        # (as if it took time to calculate the correct magic_number)
        time.sleep(0.1)
        magic_number = random.randint(0, 1000)

        # TODO: Return a newly created block
        while True:
            block = Block(signed_transaction, previous_block, magic_number)
            hash = hashlib.sha256(str(block).encode('utf-8')).hexdigest()
            if hash[0] == '0':
                return block        
            else:
                magic_number = random.randint(0, 1000)

    def make_transaction(self, from_address: str, to_address: str, coins: int) -> None:
        # IF from has enough coins in his balance
        if Node.calculate_balance(from_address, self.get_blockchain()) > coins:
            # Make a signed transfer request
            transaction = Transaction(from_address, to_address, coins)
            signed_transaction = self.sign(transaction)

            # TODO: Create a block for this transaction, and save it as our last block
            block = self.create_block(signed_transaction, self.get_blockchain())
            self._last_block = block
            pass

    def transfer_coins(self, to_address: str, coins: int) -> None:
        return self.make_transaction(self.address, to_address, coins)

    @staticmethod
    def merge_blockchains(blockchain1: Block, blockchain2: Block) -> Optional[Block]:
        # TODO: Pick the better chain and return it (How will we decide?)

        block1 = blockchain1
        block2 = blockchain2

        count1 : int = 0
        while block1.previous_block is not None:
            block1 = block1.previous_block
            count1 += 1

        count2 : int = 0
        while block2.previous_block is not None:
            block2 = block2.previous_block
            count2 += 1

        return blockchain1 if count1 > count2 else blockchain2

    @staticmethod
    def calculate_balance(node_address, blockchain):
        balance = 0
        block = blockchain  # The blockchain is a reference to the last block

        while block is not None:
            # TODO: Update the balance
            # Hint: Here is the implementation for the previous version, before we started using blocks:
            transaction: Transaction = block.signed_transaction.transaction
            if transaction.to_address == node_address:
                balance += transaction.coins
            if transaction.from_address == node_address:
                balance -= transaction.coins

            block = block.previous_block
        return balance

    def sign(self, transaction: Transaction) -> SignedTransaction:
        signature = f"signed_by_{self.address}"
        return SignedTransaction(transaction, signature)

    def add_node(self, node: 'Node'):
        self._other_nodes.append(node)

    def pull_blockchains_from_other_nodes(self):
        # For each node I know about
        for node in self._other_nodes:

            # Ask that node what blockchain (what history) it knows about
            other_blockchain = node.get_blockchain()

            # If it has any history
            if other_blockchain is not None:
                # Merge the blockchains (hint: what if they are not the same?)
                merged_blockchain = Node.merge_blockchains(self.get_blockchain(), other_blockchain)

                if merged_blockchain is not None:
                    # Set my blockchain to the better (merged) blockchain
                    self._last_block = merged_blockchain
