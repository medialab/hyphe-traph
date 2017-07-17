# =============================================================================
# Link Store Header
# =============================================================================
#
# Class representing the header of the Link Store buffer. This header can be
# used to store various metadata and/or state.
#
import struct

# Binary format
# -
# NOTE: Since python mimics C struct, the block size should be respecting
# some rules (namely have even addresses or addresses divisble by 4 on some
# architecture).
LINK_STORE_HEADER_FORMAT = 'BBxxxxxxQQQQII'

# Header blocks
# -
# We are retaining at least one header block so we can keep the 0 block address
# as a NULL pointer and be able to store some metadata about the structure.
LINK_STORE_HEADER_BLOCKS = 1

# Positions


# Main class
class LinkStoreHeader(object):
    pass
