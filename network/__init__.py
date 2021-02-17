#!/usr/bin/python3


from .state import Chain, TxHistory

__all__ = ["chain", "history"]

# rpc = Rpc()
history = TxHistory()
chain = Chain()
