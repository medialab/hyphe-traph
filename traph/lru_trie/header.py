# =============================================================================
# LRU Trie Header
# =============================================================================
#
# Class representing the header of the LRU Trie buffer. This header can be
# used to store various metadata and/or state.
#
import struct

from traph.version import __version__ as TRAPH_VERSION

# Binary format
# -
# NOTE: Since python mimics C struct, the block size should be respecting
# some rules (namely have even addresses or addresses divisible by 4 on some
# architecture).
LRU_TRIE_HEADER_FORMAT = 'I12p112x'
LRU_TRIE_HEADER_BLOCK_SIZE = struct.calcsize(LRU_TRIE_HEADER_FORMAT)

# Header blocks
# -
# We are retaining at least one header block so we can keep the 0 block address
# as a NULL pointer and be able to store some metadata about the structure.
LRU_TRIE_HEADER_BLOCKS = 1

# Positions
LRU_TRIE_HEADER_LAST_WEBENTITY_ID = 0
LRU_TRIE_HEADER_TRAPH_VERSION = 1


# Main class
class LRUTrieHeader(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, storage):

        # Properties
        self.storage = storage
        self.data = [
            0,              # Last webentity id
            TRAPH_VERSION   # Traph version
        ]

        self.__ensure()
        self.read()

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s'
            ' version=%(version)s'
            ' last_webentity_id=%(last_webentity_id)s>'
        ) % {
            'class_name': class_name,
            'version': self.get_version(),
            'last_webentity_id': self.last_webentity_id(),
        }

    def __ensure(self):
        block = 0

        empty_data = struct.pack(LRU_TRIE_HEADER_FORMAT, *self.data)

        while block < LRU_TRIE_HEADER_BLOCKS:
            data = self.storage.read(block)

            if not data:
                self.storage.write(empty_data, block)

            block += self.storage.block_size

    # =========================================================================
    # Utilities
    # =========================================================================

    # Method used to unpack data
    def unpack(self, data):
        return list(struct.unpack(LRU_TRIE_HEADER_FORMAT, data))

    # Method used to set a switch to another block
    def read(self):
        self.data = self.unpack(self.storage.read(0))

    # Method used to pack the node to binary form
    def pack(self):
        return struct.pack(LRU_TRIE_HEADER_FORMAT, *self.data)

    # Method used to write the node's data to storage
    def write(self):
        self.storage.write(self.pack(), 0)

    # =========================================================================
    # Getters/Setters
    # =========================================================================
    def last_webentity_id(self):
        return self.data[LRU_TRIE_HEADER_LAST_WEBENTITY_ID]

    def set_last_webentity_id(self, last_id):
        self.data[LRU_TRIE_HEADER_LAST_WEBENTITY_ID] = last_id

    def increment_last_webentity_id_by(self, number):
        self.data[LRU_TRIE_HEADER_LAST_WEBENTITY_ID] += number

    def increment_last_webentity_id(self):
        self.data[LRU_TRIE_HEADER_LAST_WEBENTITY_ID] += 1

    def get_version(self):
        return self.data[LRU_TRIE_HEADER_TRAPH_VERSION]
