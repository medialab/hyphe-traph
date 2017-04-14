# =============================================================================
# LRU Trie Node
# =============================================================================
#
# Class representing a single node from the LRU trie.
#
import struct

# Binary format
# NOTE: the format may induce some padding to avoid odd numbers for performance
LRU_TRIE_NODE_FORMAT = 'BBBBIIIIIIIII'
LRU_TRIE_NODE_BLOCK_SIZE = 40

# Positions
LRU_TRIE_NODE_CHAR = 0
LRU_TRIE_NODE_NEXT_BLOCK = 4


class LRUTrieNode(object):

    def __init__(self, char=None, block=None, binary_data=None):

        # Properties
        if binary_data:
            self.read(binary_data)
        else:
            self.data = [
                char, # Character
                0,    # Flags
                0,    # Flags
                0,    # Flags
                0,    # Next block
                0,    # Child block
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ]

        self.block = block


    # Method used to read new data
    def read(self, binary_data):
        self.data = list(struct.unpack(LRU_TRIE_NODE_FORMAT, binary_data))

    # Method used to pack the node to binary form
    def pack(self):
        return struct.pack(LRU_TRIE_NODE_FORMAT, *self.data)

    # Method used to retrieve the node's char
    def char(self):
        return self.data[LRU_TRIE_NODE_CHAR]

    # Method used to know whether the next block is set
    def hasNext(self):
        return self.data[LRU_TRIE_NODE_NEXT_BLOCK] != 0

    # Method used to retrieve the next block
    def next(self):
        block = self.data[LRU_TRIE_NODE_NEXT_BLOCK]

        if block == 0:
            return None

        return block

    # Method used to set a sibling
    def setNext(self, block):
        self.data[LRU_TRIE_NODE_NEXT_BLOCK] = block
