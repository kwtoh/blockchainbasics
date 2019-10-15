import random
from dataclasses import dataclass
from typing import List, Optional
import nacl.signing


@dataclass
class Transaction:
    from_address: Optional[str]  # For the initial transaction, the from_address will be None
    to_address: str
    coins: int

@dataclass
class SignedTransaction:
    transaction: Transaction
    signature: str
    

class Node:
    def __init__(self, other_nodes: List['Node'] = None, initial_coins: int = None):
        self._signed_transactions: List[SignedTransaction] = []
        self.address = random.randint(0, 1000)
        self._other_nodes: List[Node] = []
        self._signing_key = nacl.signing.SigningKey.generate()

        # If this is the first node
        if other_nodes is None and initial_coins is not None:
            # TODO: Create an initial transaction (from_address=None) and save it to the _signed_transactions list
            signed = SignedTransaction(Transaction(None, self.address, initial_coins), "signature")
            self._signed_transactions.append(signed)
            pass

        # If this is not the first node
        if other_nodes is not None and initial_coins is None:
            # TODO: Save the other_nodes
            self._other_nodes = other_nodes
            pass

    def calculate_balance(self, node_address) -> int:
        balance = 0

        # Go over all transactions
        for signed_transaction in self._signed_transactions:
            # TODO: If node_address GOT coins or SENT coins in this transaction,
            #  and update the balance accordingly.
            if signed_transaction.transaction.to_address is node_address:
                balance += signed_transaction.transaction.coins
            elif signed_transaction.transaction.from_address is node_address:
                balance -= signed_transaction.transaction.coins

            pass

        # Return the calculate balance for node_address
        return balance

    def make_transaction(self, from_address: str, to_address: str, coins: int) -> None:
        # IF from has enough coins in his balance
        if self.calculate_balance(from_address) >= coins:
            # TODO: Make a new signed transaction and save it to the _signed_transactions list
            new_trans = SignedTransaction(Transaction(from_address, to_address, coins), "signature")
            self._signed_transactions.append(new_trans)
            pass

    def transfer_coins(self, to_address: str, coins: int) -> None:
        return self.make_transaction(self.address, to_address, coins)

    def pull_transactions_from_other_nodes(self):
        # TODO (bonus) : For every node in self._other_nodes,
        #  If that node knows about a SignedTransaction that this node doesn't know about,
        #  Then copy that SignedTransaction to this node
        for node in self._other_nodes:
            for transaction in node._signed_transactions:
                if transaction not in self._signed_transactions:
                    self._signed_transactions.append(transaction)