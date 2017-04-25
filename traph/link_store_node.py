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

# Binary format
# -
# NOTE: Since python mimics C struct, the block size should be respecting
# some rules (namely have even addresses or addresses divisble by 4 on some
# architecture).
# -
# Reference: http://stackoverflow.com/questions/2611858/
#   struct-error-unpack-requires-a-string-argument-of-length-4
# -
# TODO: When the format is stabilized, we should order the bytes correctly as
# with a C struct to optimize block size & save up some space.
LINK_STORE_NODE_FORMAT = '2Q1H'
LINK_STORE_NODE_BLOCK_SIZE = struct.calcsize(LINK_STORE_NODE_FORMAT)

# Header blocks
# -
# We are retaining at least one header block so we can keep the 0 block address
# as a NULL pointer and be able to store some metadata about the structure.
LINK_STORE_NODE_HEADER_BLOCKS = 1

# Positions
LINK_STORE_NODE_TARGET = 0
LINK_STORE_NODE_NEXT = 1
LINK_STORE_NODE_WEIGHT = 2


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
            0   # Weight
        ]

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name) target=%(target)s'
            ' next=%(next)s weight=%(weight)s>'
        ) % {
            'class_name': class_name,
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
        return self.block == LINK_STORE_NODE_HEADER_BLOCKS
