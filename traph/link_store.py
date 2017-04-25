# =============================================================================
# Link Store Class
# =============================================================================
#
# Class representing the structure storing the links as linked list of stubs.
#
from link_store_node import LinkStoreNode


class LinkStore(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, storage):

        # Properties
        self.storage = storage

    # =========================================================================
    # Internal methods
    # =========================================================================

    # Method returning a node
    def __node(self, **kwargs):
        return LinkStoreNode(self.storage, **kwargs)
