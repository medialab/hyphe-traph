# =============================================================================
# LRU Trie Node
# =============================================================================
#
# Class representing a single node from the LRU trie.
#
# Note that it should be possible to speed up targeted updates by only
# writing the updated fields (typically when setting a pointer).
#
# TODO: we can be more compact for some things
#
import struct
from traph.lru_trie.header import LRU_TRIE_HEADER_BLOCKS
from traph.helpers import detailed_chunks_iter

# Binary format
# -
# NOTE: Since python mimics C struct, the block size should be respecting
# some rules (namely have even addresses or addresses divisble by 4 on some
# architecture).

# TODO: it's possible to differentiate the tail's blocks format if needed
LRU_TRIE_NODE_FORMAT = '75pBI6Q'
LRU_TRIE_NODE_BLOCK_SIZE = struct.calcsize(LRU_TRIE_NODE_FORMAT)
LRU_TRIE_FIRST_DATA_BLOCK = LRU_TRIE_HEADER_BLOCKS * LRU_TRIE_NODE_BLOCK_SIZE

# NOTE: this MUST be 1 less than the number above because varchars or
# pascal strings (hence the "p") need one byte of information to encode
# the stored string's length
# NOTE: varchars are limited to 255 characters. If we want heavier blocks
# we'll need to split the string into two varchars (but I would strongly
# advise against block fattening since we are currently in the sweet spot).
LRU_TRIE_STEM_SIZE = 74

# Node Positions
LRU_TRIE_NODE_STEM = 0
LRU_TRIE_NODE_FLAGS = 1
LRU_TRIE_NODE_WEBENTITY = 2
LRU_TRIE_NODE_LEFT_BLOCK = 3
LRU_TRIE_NODE_RIGHT_BLOCK = 4
LRU_TRIE_NODE_CHILD_BLOCK = 5
LRU_TRIE_NODE_PARENT_BLOCK = 6
LRU_TRIE_NODE_OUTLINKS_BLOCK = 7
LRU_TRIE_NODE_INLINKS_BLOCK = 8

LRU_TRIE_NODE_REGISTERS = 7  # 8 - flags

# Flags (Currently allocating 8/8 bits)
LRU_TRIE_NODE_FLAG_PAGE = 0
LRU_TRIE_NODE_FLAG_CRAWLED = 1
LRU_TRIE_NODE_FLAG_LINKED = 2
LRU_TRIE_NODE_FLAG_DELETED = 3
LRU_TRIE_NODE_FLAG_WEBENTITY_CREATION_RULE = 4
LRU_TRIE_NODE_FLAG_HAS_TAIL = 5
LRU_TRIE_NODE_FLAG_IS_TAIL = 6
LRU_TRIE_NODE_FLAG_NO_CHILD_WEBENTITIES = 7

# NO_CHILD_WEBENTITIES is on by default:
# Indeed, this was required not to bump a major version and ensure
# compatibility with older corpora
DEFAULT_FLAGS_VALUE = 0 | (1 << LRU_TRIE_NODE_FLAG_NO_CHILD_WEBENTITIES)


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
    def __init__(self, storage, stem=None, block=None, data=None):

        # Properties
        self.storage = storage
        self.block = None
        self.exists = False
        self.tail = ''

        # Loading node from storage
        if block is not None:
            self.read(block)

        # Creating node from raw data
        elif data:
            self.data = self.unpack(data)
        else:
            self.__set_default_data(stem)

    def __set_default_data(self, stem=None):
        self.data = ['', DEFAULT_FLAGS_VALUE] + [0] * LRU_TRIE_NODE_REGISTERS

        if stem is not None:
            self.set_stem(stem)

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s "%(stem)s"'
            ' block=%(block)s exists=%(exists)s has_tail=%(has_tail)s'
            ' parent=%(parent)s child=%(child)s left=%(left)s right=%(right)s'
            ' out=%(outlinks)s we=%(webentity)s wecr=%(webentity_creation_rule)s>'
        ) % {
            'class_name': class_name,
            'stem': self.stem(),
            'block': self.block,
            'exists': str(self.exists),
            'has_tail': str(self.has_tail()),
            'page': self.is_page(),
            'crawled': self.is_crawled(),
            'parent': self.parent(),
            'child': self.child(),
            'left': self.left(),
            'right': self.right(),
            'outlinks': self.outlinks(),
            'webentity': self.webentity(),
            'webentity_creation_rule': self.has_webentity_creation_rule()
        }

    # =========================================================================
    # Utilities
    # =========================================================================

    # unpack data
    def unpack(self, data):
        return list(struct.unpack(LRU_TRIE_NODE_FORMAT, data))

    # set a switch to another block
    def read(self, block):
        data = self.storage.read(block)

        if data is None:
            self.exists = False
            self.__set_default_data()
            self.tail = ''
        else:
            self.exists = True
            self.data = self.unpack(data)
            self.block = block
            self.tail = ''

            # Reading the tail recursively
            # TODO: it's possible not to read the tail in some cases
            # TODO: it might be possible to "stream" the tail when performing
            # BST comparison (probably overkill)
            if self.has_tail():
                chunks = []

                while True:
                    data = struct.unpack(LRU_TRIE_NODE_FORMAT, self.storage.read())
                    chars = data[LRU_TRIE_NODE_STEM]

                    chunks.append(chars)

                    if not test(data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_HAS_TAIL):
                        break

                self.tail = ''.join(chunks)

    # re-acquiring data from storage because it may have changed
    def refresh(self):
        self.read(self.block)

    # pack the node to binary form
    def pack(self):
        return struct.pack(LRU_TRIE_NODE_FORMAT, *self.data)

    # write the node's data to storage
    def write(self):
        block = self.storage.write(self.pack(), self.block)
        self.block = block

        # Writing the tail recursively
        # NOTE: does not work on subsequent updates
        if self.tail and not self.exists:
            for is_last, chunk in detailed_chunks_iter(LRU_TRIE_STEM_SIZE, self.tail):
                data = [chunk, DEFAULT_FLAGS_VALUE] + [0] * LRU_TRIE_NODE_REGISTERS

                flag(data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_IS_TAIL)

                if not is_last:
                    flag(data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_HAS_TAIL)

                self.storage.write(
                    struct.pack(
                        LRU_TRIE_NODE_FORMAT,
                        *data
                    )
                )

        self.exists = True

    # Method returning whether this node is the root
    def is_root(self):
        return self.block == LRU_TRIE_FIRST_DATA_BLOCK

    # =========================================================================
    # Flags methods
    # =========================================================================
    def is_page(self):
        return test(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_PAGE)

    def flag_as_page(self):
        flag(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_PAGE)

    def unflag_as_page(self):
        unflag(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_PAGE)

    def is_crawled(self):
        return test(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_CRAWLED)

    def flag_as_crawled(self):
        flag(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_CRAWLED)

    def unflag_as_crawled(self):
        unflag(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_CRAWLED)

    def has_webentity_creation_rule(self):
        return test(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_WEBENTITY_CREATION_RULE)

    def flag_as_webentity_creation_rule(self):
        flag(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_WEBENTITY_CREATION_RULE)

    def unflag_as_webentity_creation_rule(self):
        unflag(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_WEBENTITY_CREATION_RULE)

    def has_tail(self):
        return test(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_HAS_TAIL)

    def flag_as_having_tail(self):
        flag(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_HAS_TAIL)

    def is_tail(self):
        return test(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_IS_TAIL)

    def can_have_child_webentities(self):
        return not test(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_NO_CHILD_WEBENTITIES)

    def flag_can_have_child_webentities(self):
        unflag(self.data, LRU_TRIE_NODE_FLAGS, LRU_TRIE_NODE_FLAG_NO_CHILD_WEBENTITIES)

    # =========================================================================
    # Stem methods
    # =========================================================================

    def stem(self):
        chars = self.data[LRU_TRIE_NODE_STEM]

        return chars + self.tail

    def set_stem(self, stem):

        # If the stem can be stored in our block, things are simple
        if len(stem) <= LRU_TRIE_STEM_SIZE:
            self.data[LRU_TRIE_NODE_STEM] = stem

        # Else, we need to chunk the stem and write a tail
        else:
            self.data[LRU_TRIE_NODE_STEM] = stem[:LRU_TRIE_STEM_SIZE]

            self.tail = stem[LRU_TRIE_STEM_SIZE:]
            self.flag_as_having_tail()

    # =========================================================================
    # Binary Treee block methods
    # =========================================================================

    # know whether the left block is set
    def has_left(self):
        return self.data[LRU_TRIE_NODE_LEFT_BLOCK] != 0

    # retrieve the left block
    def left(self):
        block = self.data[LRU_TRIE_NODE_LEFT_BLOCK]

        if block < LRU_TRIE_FIRST_DATA_BLOCK:
            return None

        return block

    # set a sibling
    def set_left(self, block):
        if block < LRU_TRIE_FIRST_DATA_BLOCK:
            raise LRUTrieNodeUsageException('Left node cannot be the root.')

        self.data[LRU_TRIE_NODE_LEFT_BLOCK] = block

    # read the left sibling
    def read_left(self):
        if not self.has_left():
            raise LRUTrieNodeTraversalException('Node has no left sibling.')

        self.read(self.left())

    # get left node
    def left_node(self):
        if not self.has_left():
            raise LRUTrieNodeTraversalException('Node has no left sibling.')

        return LRUTrieNode(self.storage, block=self.left())

    # know whether the left block is set
    def has_right(self):
        return self.data[LRU_TRIE_NODE_RIGHT_BLOCK] != 0

    # retrieve the right block
    def right(self):
        block = self.data[LRU_TRIE_NODE_RIGHT_BLOCK]

        if block < LRU_TRIE_FIRST_DATA_BLOCK:
            return None

        return block

    # set a sibling
    def set_right(self, block):
        if block < LRU_TRIE_FIRST_DATA_BLOCK:
            raise LRUTrieNodeUsageException('right node cannot be the root.')

        self.data[LRU_TRIE_NODE_RIGHT_BLOCK] = block

    # read the right sibling
    def read_right(self):
        if not self.has_right():
            raise LRUTrieNodeTraversalException('Node has no right sibling.')

        self.read(self.right())

    # get right node
    def right_node(self):
        if not self.has_right():
            raise LRUTrieNodeTraversalException('Node has no right sibling.')

        return LRUTrieNode(self.storage, block=self.right())

    # =========================================================================
    # Child block methods
    # =========================================================================

    # know whether the child block is set
    def has_child(self):
        return self.data[LRU_TRIE_NODE_CHILD_BLOCK] != 0

    # retrieve the child block
    def child(self):
        block = self.data[LRU_TRIE_NODE_CHILD_BLOCK]

        if block < LRU_TRIE_FIRST_DATA_BLOCK:
            return None

        return block

    # set a child
    def set_child(self, block):
        if block < LRU_TRIE_FIRST_DATA_BLOCK:
            raise LRUTrieNodeUsageException('Child node cannot be the root.')

        self.data[LRU_TRIE_NODE_CHILD_BLOCK] = block

    # read the child
    def read_child(self):
        if not self.has_child():
            raise LRUTrieNodeTraversalException('Node has no child.')

        self.read(self.child())

    # get child node
    def child_node(self):
        if not self.has_child():
            raise LRUTrieNodeTraversalException('Node has no child.')

        return LRUTrieNode(self.storage, block=self.child())

    # =========================================================================
    # Parent block methods
    # =========================================================================

    # know whether the parent block is set
    def has_parent(self):
        return self.data[LRU_TRIE_NODE_PARENT_BLOCK] != 0

    # retrieve the parent block
    def parent(self):
        block = self.data[LRU_TRIE_NODE_PARENT_BLOCK]

        return block

    # set a parent
    def set_parent(self, block):
        self.data[LRU_TRIE_NODE_PARENT_BLOCK] = block

    # read the parent
    def read_parent(self):
        parent = self.parent()

        if parent < LRU_TRIE_FIRST_DATA_BLOCK:
            raise LRUTrieNodeTraversalException('Node has no parent (root).')

        self.read(self.parent())

    # get parent node
    def parent_node(self):
        return LRUTrieNode(self.storage, block=self.parent())

    # =========================================================================
    # Outlinks block methods
    # =========================================================================

    # know whether the outlinks block is set
    def has_outlinks(self):
        return self.data[LRU_TRIE_NODE_OUTLINKS_BLOCK] != 0

    # retrieve the outlinks block
    def outlinks(self):
        return self.data[LRU_TRIE_NODE_OUTLINKS_BLOCK]

    # set the outlinks block
    def set_outlinks(self, block):
        self.data[LRU_TRIE_NODE_OUTLINKS_BLOCK] = block

    # =========================================================================
    # Inlinks block methods
    # =========================================================================

    # know whether the outlinks block is set
    def has_inlinks(self):
        return self.data[LRU_TRIE_NODE_INLINKS_BLOCK] != 0

    # retrieve the inlinks block
    def inlinks(self):
        return self.data[LRU_TRIE_NODE_INLINKS_BLOCK]

    # set the inlinks block
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

        return self.data[offset]

    def set_links(self, block, out=True):
        offset = LRU_TRIE_NODE_OUTLINKS_BLOCK

        if not out:
            offset = LRU_TRIE_NODE_INLINKS_BLOCK

        self.data[offset] = block

    # =========================================================================
    # WebEntity methods
    # =========================================================================

    # know whether the node has a webentity flag
    def has_webentity(self):
        return self.data[LRU_TRIE_NODE_WEBENTITY] != 0

    # retrieve the webentity id of the flag
    def webentity(self):
        weid = self.data[LRU_TRIE_NODE_WEBENTITY]

        if weid == 0:
            return None

        return weid

    # set the webentity flag
    def set_webentity(self, weid):
        self.data[LRU_TRIE_NODE_WEBENTITY] = weid

    # remove the tie between the node (ie. prefix) and the webentity
    def unset_webentity(self):
        self.data[LRU_TRIE_NODE_WEBENTITY] = 0
