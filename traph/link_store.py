# =============================================================================
# Link Store Class
# =============================================================================
#
# Class representing the structure storing the links as linked list of stubs.
#
from itertools import chain
from link_store_node import LinkStoreNode
from link_store_header import LINK_STORE_HEADER_BLOCKS


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
        return self.__node(block=LINK_STORE_HEADER_BLOCKS)

    # Method ensuring we wrote the headers
    def __ensure_headers(self):
        header_block = 0

        while header_block < LINK_STORE_HEADER_BLOCKS:
            header_node = self.__node(block=header_block)

            if not header_node.exists:
                header_node.write()

            header_block += 1

    # =========================================================================
    # Mutation methods
    # =========================================================================
    def add_link(self, source_node, target_block):

        # If the node does not have outlinks yet
        if not source_node.has_outlinks():
            link_node = self.__node()
            link_node.set_target(target_block)
            link_node.write()

            source_node.set_outlinks(link_node.block)
            source_node.write()

            return

        # Else:
        link_node = self.__node(block=source_node.outlinks())

        if not link_node.exists:
            raise LinkStoreTraversalException('Block does not exist.')

        # We go through the linked list to find matching link
        while link_node.target() != target_block and link_node.has_next():
            link_node.read_next()

        # If we did not find a matching link, we add it
        if link_node.target() != target_block:
            sibling = self.__node()
            sibling.set_target(target_block)
            sibling.write()
            link_node.set_next(sibling.block)
            link_node.write()

        # Else we just increment the weight of the existing one
        else:
            link_node.increment_weight()
            link_node.write()

    def add_links(self, source_node, target_blocks):
        target_blocks = iter(target_blocks)

        try:
            first_target_block = next(target_blocks)
        except StopIteration:
            return

        # If the node does not have outlinks yet
        if not source_node.has_outlinks():
            link_node = self.__node()
            link_node.set_target(first_target_block)
            link_node.write()

            source_node.set_outlinks(link_node.block)
            source_node.write()

            first_target_block = None

        # Finding the current
        link_nodes = self.link_nodes_iter(source_node.outlinks())
        link_nodes_index = {}
        last_link_node = None

        for link_node in link_nodes:
            link_nodes_index[link_node.target()] = link_node
            last_link_node = link_node

        if first_target_block:
            target_blocks = chain([first_target_block], target_blocks)

        # Adding new targets
        for target_block in target_blocks:

            if target_block in link_nodes_index:
                link_node = link_nodes_index[target_block]
                link_node.increment_weight()
                link_node.write()
            else:
                link_node = self.__node()
                link_node.set_target(target_block)
                link_node.write()

                link_nodes_index[target_block] = link_node

                last_link_node.set_next(link_node.block)
                last_link_node = link_node

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
