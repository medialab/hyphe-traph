# =============================================================================
# Link Store Node
# =============================================================================
#
# Class representing a single node from the Link Store.
#
# Note: it could be useful to create an abstract Node class for both the
# LinkStoreNode and the LRUTrieNode but I thinks this is overkill for the
# time being.
#
import struct
from traph.link_store.header import LINK_STORE_HEADER_BLOCKS
from traph.lru_trie.node import LRU_TRIE_FIRST_DATA_BLOCK

# Binary format
# -
# NOTE: Since python mimics C struct, the block size should be respecting
# some rules (namely have even addresses or addresses divisble by 4 on some
# architecture).
LINK_STORE_NODE_FORMAT = 'QQH'
LINK_STORE_NODE_BLOCK_SIZE = struct.calcsize(LINK_STORE_NODE_FORMAT)
LINK_STORE_FIRST_DATA_BLOCK = LINK_STORE_HEADER_BLOCKS * LINK_STORE_NODE_BLOCK_SIZE

# Positions
LINK_STORE_NODE_TARGET = 0
LINK_STORE_NODE_NEXT = 1
LINK_STORE_NODE_WEIGHT = 2


# Exceptions
class LinkStoreNodeTraversalException(Exception):
    pass


class LinkStoreNodeUsageException(Exception):
    pass


# Main class
class LinkStoreNode(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, storage, block=None, data=None):

        # Properties
        self.storage = storage
        self.block = None
        self.exists = False

        # Loading node from storage
        if block is not None:
            self.read(block)

        # Creating node from raw data
        elif data:
            self.data = self.unpack(data)
        else:
            self.__set_default_data()

    def __set_default_data(self):
        self.data = [
            0,  # Target
            0,  # Next
            1   # Weight
        ]

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s block=%(block)s exists=%(exists)s'
            ' target=%(target)s next=%(next)s weight=%(weight)s>'
        ) % {
            'class_name': class_name,
            'block': self.block,
            'exists': self.exists,
            'target': self.target(),
            'next': self.next(),
            'weight': self.weight()
        }

    # =========================================================================
    # Utilities
    # =========================================================================

    # Method used to unpack data
    def unpack(self, data):
        return list(struct.unpack(LINK_STORE_NODE_FORMAT, data))

    # Method used to set a switch to another block
    def read(self, block):
        data = self.storage.read(block)

        if data is None:
            self.exists = False
            self.__set_default_data()
        else:
            self.exists = True
            self.data = self.unpack(data)
            self.block = block

    # Method used to pack the node to binary form
    def pack(self):
        return struct.pack(LINK_STORE_NODE_FORMAT, *self.data)

    # Method used to write the node's data to storage
    def write(self):
        block = self.storage.write(self.pack(), self.block)
        self.block = block
        self.exists = True

    # Method returning whether this node is the root
    def is_root(self):
        return self.block == LINK_STORE_FIRST_DATA_BLOCK

    # =========================================================================
    # Next block methods
    # =========================================================================

    # Method used to know whether the next block is set
    def has_next(self):
        return self.data[LINK_STORE_NODE_NEXT] != 0

    # Method used to retrieve the next block
    def next(self):
        block = self.data[LINK_STORE_NODE_NEXT]

        if block < LINK_STORE_FIRST_DATA_BLOCK:
            return None

        return block

    # Method used to set a sibling
    def set_next(self, block):
        if block < LINK_STORE_FIRST_DATA_BLOCK:
            raise LinkStoreNodeUsageException('Next node cannot be the root.')

        self.data[LINK_STORE_NODE_NEXT] = block

    # Method used to read the next sibling
    def read_next(self):
        if not self.has_next():
            raise LinkStoreNodeTraversalException('Node has no next sibling.')

        self.read(self.next())

    # Method used to get next node
    def next_node(self):
        if not self.has_next():
            raise LinkStoreNodeTraversalException('Node has no next sibling.')

        return LRUTrieNode(self.storage, block=self.next())

    # =========================================================================
    # Target block methods
    # =========================================================================

    # Method used to know whether the target block is set
    def has_target(self):
        return self.data[LINK_STORE_NODE_TARGET] != 0

    # Method used to retrieve the target block
    def target(self):
        block = self.data[LINK_STORE_NODE_TARGET]

        if block < LRU_TRIE_FIRST_DATA_BLOCK:
            return None

        return block

    # Method used to set the target block
    def set_target(self, block):
        if block < LRU_TRIE_FIRST_DATA_BLOCK:
            raise LinkStoreNodeUsageException(
                'Target node cannot be the root.'
            )

        self.data[LINK_STORE_NODE_TARGET] = block

    # =========================================================================
    # Weight methods
    # =========================================================================
    def weight(self):
        return self.data[LINK_STORE_NODE_WEIGHT]

    def set_weight(self, weight):
        self.data[LINK_STORE_NODE_WEIGHT] = weight

    def increment_weight(self):
        self.data[LINK_STORE_NODE_WEIGHT] += 1
