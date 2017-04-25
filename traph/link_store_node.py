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
# Reference: http://stackoverflow.com/questions/2611858/struct-error-unpack-requires-a-string-argument-of-length-4
# -
# TODO: When the format is stabilized, we should order the bytes correctly as
# with a C struct to optimize block size & save up some space.
LINK_STORE_NODE_FORMAT = '2Q1H'
LINK_STORE_NODE_SIZE = struct.calcsize(LINK_STORE_NODE_FORMAT)

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
        self.data = (
            char or 0,  # Target
            0,          # Next
            0          # Weight
        )
