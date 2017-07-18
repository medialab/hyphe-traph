# =============================================================================
# LRU Trie Node
# =============================================================================
#
# Class representing a single node from the LRU trie.
#
# Note that it should be possible to speed up targeted updates by only
# writing the updated fields (typically when setting a pointer).
#
import struct
from lru_trie_header import LRU_TRIE_HEADER_BLOCKS

# TODO: we can be more compact for some things

# Binary format
# -
# NOTE: Since python mimics C struct, the block size should be respecting
# some rules (namely have even addresses or addresses divisble by 4 on some
# architecture).
LRU_TRIE_NODE_FORMAT = 'BBxxIQQQQQ'
LRU_TRIE_NODE_BLOCK_SIZE = struct.calcsize(LRU_TRIE_NODE_FORMAT)

# Header blocks
# -
# We are retaining at least one header block so we can keep the 0 block address
# as a NULL pointer and be able to store some metadata about the structure.
LRU_TRIE_NODE_HEADER_BLOCKS = 1

# Node Positions
LRU_TRIE_NODE_CHAR = 0
LRU_TRIE_NODE_FLAGS = 1
LRU_TRIE_NODE_WEBENTITY = 2
LRU_TRIE_NODE_NEXT_BLOCK = 3
LRU_TRIE_NODE_CHILD_BLOCK = 4
LRU_TRIE_NODE_PARENT_BLOCK = 5
LRU_TRIE_NODE_OUTLINKS_BLOCK = 6
LRU_TRIE_NODE_INLINKS_BLOCK = 7

# Flags (Currently allocating 5/8 bits)
LRU_TRIE_NODE_FLAG_PAGE = 0
LRU_TRIE_NODE_FLAG_CRAWLED = 1
LRU_TRIE_NODE_FLAG_LINKED = 2
LRU_TRIE_NODE_FLAG_DELETED = 3
LRU_TRIE_NODE_FLAG_WEBENTITY_CREATION_RULE = 4


# Helpers
def flag(data, register, pos):
    data[register] |= (1 << pos)


def unflag(data, register, pos):
    data[register] &= ~(1 << pos)


def test(data, register, pos):
    return bool((data[register] >> pos) & 1)


# Exceptions
class LRUTrieNodeTraversalException(Exception):
    pass


class LRUTrieNodeUsageException(Exception):
    pass


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
            0,          # Webentity
            0,          # Next block
            0,          # Child block
            0,          # Parent block
            0,          # Outlinks block
            0,          # Inlinks block
        ]

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s "%(char)s"'
            ' block=%(block)s exists=%(exists)s'
            ' parent=%(parent)s child=%(child)s next=%(next)s'
            ' out=%(outlinks)s we=%(webentity)s wecr=%(webentity_creation_rule)s>'
        ) % {
            'class_name': class_name,
            'char': self.char_as_str(),
            'block': self.block,
            'exists': str(self.exists),
            'parent': self.parent(),
            'child': self.child(),
            'next': self.next(),
            'outlinks': self.outlinks(),
            'webentity': self.webentity(),
            'webentity_creation_rule': self.has_webentity_creation_rule()
        }

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
            self.exists = True
            self.data = self.unpack(data)
            self.block = block

    # Method used to pack the node to binary form
    def pack(self):
        return struct.pack(LRU_TRIE_NODE_FORMAT, *self.data)

    # Method used to write the node's data to storage
    def write(self):
        block = self.storage.write(self.pack(), self.block)
        self.block = block
        self.exists = True

    # Method returning whether this node is the root
    def is_root(self):
        return self.block == LRU_TRIE_NODE_HEADER_BLOCKS

    # =========================================================================
    # Flags methods
    # =========================================================================
    def is_page(self):
        return test(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_PAGE)

    def flag_as_page(self):
        flag(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_PAGE)

    def unflag_as_page(self):
        unflag(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_PAGE)

    def has_webentity_creation_rule(self):
        return test(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_WEBENTITY_CREATION_RULE)

    def flag_as_webentity_creation_rule(self):
        flag(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_WEBENTITY_CREATION_RULE)

    def unflag_as_webentity_creation_rule(self):
        unflag(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_WEBENTITY_CREATION_RULE)

    # =========================================================================
    # Character methods
    # =========================================================================

    # Method used to retrieve the node's char
    def char(self):
        return self.data[LRU_TRIE_NODE_CHAR]

    # Method used to retrieve the node's char as a string
    def char_as_str(self):
        return chr(self.char())

    # Method used to set the node's char
    def set_char(self, char):
        self.data[LRU_TRIE_NODE_CHAR] = char

    # =========================================================================
    # Next block methods
    # =========================================================================

    # Method used to know whether the next block is set
    def has_next(self):
        return self.data[LRU_TRIE_NODE_NEXT_BLOCK] != 0

    # Method used to retrieve the next block
    def next(self):
        block = self.data[LRU_TRIE_NODE_NEXT_BLOCK]

        if block < LRU_TRIE_NODE_HEADER_BLOCKS:
            return None

        return block

    # Method used to set a sibling
    def set_next(self, block):
        if block < LRU_TRIE_NODE_HEADER_BLOCKS:
            raise LRUTrieNodeUsageException('Next node cannot be the root.')

        self.data[LRU_TRIE_NODE_NEXT_BLOCK] = block

    # Method used to read the next sibling
    def read_next(self):
        if not self.has_next():
            raise LRUTrieNodeTraversalException('Node has no next sibling.')

        self.read(self.next())

    # Method used to get next node
    def next_node(self):
        if not self.has_next():
            raise LRUTrieNodeTraversalException('Node has no next sibling.')

        return LRUTrieNode(self.storage, block=self.next())

    # =========================================================================
    # Child block methods
    # =========================================================================

    # Method used to know whether the child block is set
    def has_child(self):
        return self.data[LRU_TRIE_NODE_CHILD_BLOCK] != 0

    # Method used to retrieve the child block
    def child(self):
        block = self.data[LRU_TRIE_NODE_CHILD_BLOCK]

        if block < LRU_TRIE_NODE_HEADER_BLOCKS:
            return None

        return block

    # Method used to set a child
    def set_child(self, block):
        if block < LRU_TRIE_NODE_HEADER_BLOCKS:
            raise LRUTrieNodeUsageException('Child node cannot be the root.')

        self.data[LRU_TRIE_NODE_CHILD_BLOCK] = block

    # Method used to read the child
    def read_child(self):
        if not self.has_child():
            raise LRUTrieNodeTraversalException('Node has no child.')

        self.read(self.child())

    # Method used to get child node
    def child_node(self):
        if not self.has_child():
            raise LRUTrieNodeTraversalException('Node has no child.')

        return LRUTrieNode(self.storage, block=self.child())

    # =========================================================================
    # Parent block methods
    # =========================================================================

    # Method used to retrieve the parent block
    def parent(self):
        block = self.data[LRU_TRIE_NODE_PARENT_BLOCK]

        return block

    # Method used to set a parent
    def set_parent(self, block):
        self.data[LRU_TRIE_NODE_PARENT_BLOCK] = block

    # Method used to read the parent
    def read_parent(self):
        self.read(self.parent())

    # Method used to get parent node
    def parent_node(self):
        return LRUTrieNode(self.storage, block=self.parent())

    # =========================================================================
    # Outlinks block methods
    # =========================================================================

    # Method used to know whether the outlinks block is set
    def has_outlinks(self):
        return self.data[LRU_TRIE_NODE_OUTLINKS_BLOCK] != 0

    # Method used to retrieve the outlinks block
    def outlinks(self):
        block = self.data[LRU_TRIE_NODE_OUTLINKS_BLOCK]

        if block < LRU_TRIE_NODE_HEADER_BLOCKS:
            return None

        return block

    # Method used to set the outlinks block
    def set_outlinks(self, block):
        self.data[LRU_TRIE_NODE_OUTLINKS_BLOCK] = block

    # =========================================================================
    # Inlinks block methods
    # =========================================================================

    # Method used to know whether the outlinks block is set
    def has_inlinks(self):
        return self.data[LRU_TRIE_NODE_INLINKS_BLOCK] != 0

    # Method used to retrieve the inlinks block
    def inlinks(self):
        block = self.data[LRU_TRIE_NODE_INLINKS_BLOCK]

        if block < LRU_TRIE_NODE_HEADER_BLOCKS:
            return None

        return block

    # Method used to set the inlinks block
    def set_inlinks(self, block):
        self.data[LRU_TRIE_NODE_INLINKS_BLOCK] = block

    # =========================================================================
    # Generic links block methods
    # =========================================================================
    def has_links(self, out=True):
        offset = LRU_TRIE_NODE_OUTLINKS_BLOCK

        if not out:
            offset = LRU_TRIE_NODE_INLINKS_BLOCK

        return self.data[offset] != 0

    def links(self, out=True):
        offset = LRU_TRIE_NODE_OUTLINKS_BLOCK

        if not out:
            offset = LRU_TRIE_NODE_INLINKS_BLOCK

        block = self.data[offset]

        if block < LRU_TRIE_NODE_HEADER_BLOCKS:
            return None

        return block

    def set_links(self, block, out=True):
        offset = LRU_TRIE_NODE_OUTLINKS_BLOCK

        if not out:
            offset = LRU_TRIE_NODE_INLINKS_BLOCK

        self.data[offset] = block


    # =========================================================================
    # WebEntity methods
    # =========================================================================

    # Method used to know whether the node has a webentity flag
    def has_webentity(self):
        return self.data[LRU_TRIE_NODE_WEBENTITY] != 0

    # Method used to retrieve the webentity id of the flag
    def webentity(self):
        weid = self.data[LRU_TRIE_NODE_WEBENTITY]

        if weid == 0:
            return None

        return weid

    # Method used to set the webentity flag
    def set_webentity(self, weid):
        self.data[LRU_TRIE_NODE_WEBENTITY] = weid
