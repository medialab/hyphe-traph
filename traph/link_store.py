# =============================================================================
# Link Store Class
# =============================================================================
#
# Class representing the structure storing the links as linked list of stubs.
#
from link_store_node import LinkStoreNode, LINK_STORE_NODE_HEADER_BLOCKS


# Exceptions
class LinkStoreTraversalException(Exception):
    pass


# Main class
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

    # =========================================================================
    # Mutation methods
    # =========================================================================
    def add_first_link(self, target_block):
        node = self.__node()
        node.set_target(target_block)
        node.write()

        return node.block

    def add_link(self, block, target_block):
        node = self.__node(block=block)

        if not node.exists:
            raise LinkStoreTraversalException('Block does not exist.')

        while node.target() != target_block and node.has_next():
            node.read_next()

        if node.target() != target_block:
            sibling = self.__node()
            sibling.set_target(target_block)
            sibling.write()
            node.set_next(sibling.block)
            node.write()
        else:
            node.increment_weight()
            node.write()

    # =========================================================================
    # Iteration methods
    # =========================================================================
    def link_nodes_iter(self, block):
        node = self.__node(block=block)

        if not node.exists:
            raise LinkStoreTraversalException('Block does not exist.')

        yield node

        while node.has_next():
            node.read_next()
            yield node
