# =============================================================================
# Link Store Class
# =============================================================================
#
# Class representing the structure storing the links as linked list of stubs.
#
from link_store_node import LinkStoreNode, LINK_STORE_NODE_HEADER_BLOCKS


class LinkStore(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, storage):

        # Properties
        self.storage = storage

        # Ensuring headers are written
        self.__ensure_headers()

    # =========================================================================
    # Internal methods
    # =========================================================================

    # Method returning a node
    def __node(self, **kwargs):
        return LinkStoreNode(self.storage, **kwargs)

    # Method returning the root
    def __root(self):
        return self.__node(block=LINK_STORE_NODE_HEADER_BLOCKS)

    # Method ensuring we wrote the headers
    def __ensure_headers(self):
        header_block = 0

        while header_block < LINK_STORE_NODE_HEADER_BLOCKS:
            header_node = self.__node(block=header_block)

            if not header_node.exists:
                header_node.write()

            header_block += 1
