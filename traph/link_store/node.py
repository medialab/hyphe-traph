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
# NOTE: the size of the header struct MUST match the node's one.
LINK_STORE_NODE_FORMAT = "QQ"
LINK_STORE_NODE_BLOCK_SIZE = struct.calcsize(LINK_STORE_NODE_FORMAT)
LINK_STORE_FIRST_DATA_BLOCK = LINK_STORE_HEADER_BLOCKS * LINK_STORE_NODE_BLOCK_SIZE

# Positions
LINK_STORE_NODE_TARGET = 0
LINK_STORE_NODE_PREVIOUS = 1


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
            0,  # Previous
        ]

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            "<%(class_name)s block=%(block)s exists=%(exists)s"
            " target=%(target)s previous=%(previous)s>"
        ) % {
            "class_name": class_name,
            "block": self.block,
            "exists": self.exists,
            "target": self.target(),
            "previous": self.previous(),
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
    # Previous block methods
    # =========================================================================

    # Method used to know whether the previous block is set
    def has_previous(self):
        return self.data[LINK_STORE_NODE_PREVIOUS] != 0

    # Method used to retrieve the previous block
    def previous(self):
        block = self.data[LINK_STORE_NODE_PREVIOUS]

        if block < LINK_STORE_FIRST_DATA_BLOCK:
            return None

        return block

    # Method used to set a sibling
    def set_previous(self, block):
        if block < LINK_STORE_FIRST_DATA_BLOCK:
            raise LinkStoreNodeUsageException("Previous node cannot be the root.")

        self.data[LINK_STORE_NODE_PREVIOUS] = block

    # Method used to read the previous sibling
    def read_previous(self):
        if not self.has_previous():
            raise LinkStoreNodeTraversalException("Node has no previous sibling.")

        self.read(self.previous())

    # Method used to get previous node
    def previous_node(self):
        if not self.has_previous():
            raise LinkStoreNodeTraversalException("Node has no previous sibling.")

        return LinkStoreNode(self.storage, block=self.previous())

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
            raise LinkStoreNodeUsageException("Target node cannot be the root.")

        self.data[LINK_STORE_NODE_TARGET] = block
