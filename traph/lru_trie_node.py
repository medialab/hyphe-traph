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
LRU_TRIE_NODE_CHILD_BLOCK = 5


# Main class
class LRUTrieNode(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, storage, char=None, block=None, data=None):

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
            self.__set_default_data(char)

    def __set_default_data(self, char=None):
        self.data = [
            char or 0,  # Character
            0,          # Flags
            0,          # Flags
            0,          # Flags
            0,          # Next block
            0,          # Child block
            0,
            0,
            0,
            0,
            0,
            0,
            0
        ]

    # =========================================================================
    # Utilities
    # =========================================================================

    # Method used to unpack data
    def unpack(self, data):
        return list(struct.unpack(LRU_TRIE_NODE_FORMAT, data))

    # Method used to set a switch to another block
    def read(self, block):
        data = self.storage.read(block)

        if data is None:
            self.exists = False
            self.__set_default_data()
        else:
            self.data = self.unpack(data)
            self.block = block

    # Method used to pack the node to binary form
    def pack(self):
        return struct.pack(LRU_TRIE_NODE_FORMAT, *self.data)

    # Method used to write the node's data to storage
    def write(self):
        self.storage.write(self.pack(), self.block)

    # =========================================================================
    # Character-related methods
    # =========================================================================

    # Method used to retrieve the node's char
    def char(self):
        return self.data[LRU_TRIE_NODE_CHAR]

    # Method used to set the node's char
    def set_char(self, char):
        self.data[LRU_TRIE_NODE_CHAR] = char

    # =========================================================================
    # Next block-related methods
    # =========================================================================

    # Method used to know whether the next block is set
    def has_next(self):
        return self.data[LRU_TRIE_NODE_NEXT_BLOCK] != 0

    # Method used to retrieve the next block
    def next(self):
        block = self.data[LRU_TRIE_NODE_NEXT_BLOCK]

        if block == 0:
            return None

        return block

    # Method used to set a sibling
    def set_next(self, block):
        self.data[LRU_TRIE_NODE_NEXT_BLOCK] = block

    # Method used to read the next sibling
    def read_next(self):
        if not self.has_next():
            print "TODO: traversal exception"
            return

        self.read(self.next())

    # =========================================================================
    # Child block related-methods
    # =========================================================================

    # Method used to know whether the child block is set
    def has_child(self):
        return self.data[LRU_TRIE_NODE_CHILD_BLOCK] != 0

    # Method used to retrieve the child block
    def child(self):
        block = self.data[LRU_TRIE_NODE_CHILD_BLOCK]

        if block == 0:
            return None

        return block

    # Method used to set a sibling
    def set_child(self, block):
        self.data[LRU_TRIE_NODE_CHILD_BLOCK] = block

    # Method used to read the next sibling
    def read_child(self):
        if not self.has_child():
            print "TODO: traversal exception"
            return

        self.read(self.child())

# Static properties
LRUTrieNode.block_fmt = LRU_TRIE_NODE_FORMAT
LRUTrieNode.block_size = LRU_TRIE_NODE_BLOCK_SIZE
