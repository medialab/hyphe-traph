# =============================================================================
# LRU Trie Header
# =============================================================================
#
# Class representing the header of the LRU Trie buffer. This header can be
# used to store various metadata and/or state.
#
import struct

# Binary format
# -
# NOTE: Since python mimics C struct, the block size should be respecting
# some rules (namely have even addresses or addresses divisble by 4 on some
# architecture).
LRU_TRIE_HEADER_FORMAT = 'BBxxxxxxQQQQII'

# Header blocks
# -
# We are retaining at least one header block so we can keep the 0 block address
# as a NULL pointer and be able to store some metadata about the structure.
LRU_TRIE_HEADER_BLOCKS = 1

# Positions
LRU_TRIE_HEADER_LAST_WEBENTITY_ID = 0


# Main class
class LRUTrieHeader(object):
    pass
