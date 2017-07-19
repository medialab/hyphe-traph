# =============================================================================
# Link Store Class
# =============================================================================
#
# Class representing the structure storing the links as linked list of stubs.
#
from itertools import chain
from link_store_node import LinkStoreNode, LINK_STORE_FIRST_DATA_BLOCK
from link_store_header import LinkStoreHeader


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

        # Reading headers
        self.header = LinkStoreHeader(storage)

    # =========================================================================
    # Internal methods
    # =========================================================================

    # Method returning a node
    def __node(self, **kwargs):
        return LinkStoreNode(self.storage, **kwargs)

    # Method returning the root
    # TODO: memoize or cache
    def __root(self):
        return self.__node(block=LINK_STORE_FIRST_DATA_BLOCK)

    # =========================================================================
    # Mutation methods
    # =========================================================================

    # TODO: not used for the time being
    def add_link(self, source_node, target_block, out=True):

        # If the node does not have outlinks yet
        if not source_node.has_links(out=out):
            link_node = self.__node()
            link_node.set_target(target_block)
            link_node.write()

            source_node.set_links(link_node.block, out=out)
            source_node.write()

            return

        # Else:
        link_node = self.__node(block=source_node.links(out=out))

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

    def add_links(self, source_node, target_blocks, out=True):
        target_blocks = iter(target_blocks)
        links_block = source_node.links(out=out)

        try:
            first_target_block = next(target_blocks)
        except StopIteration:
            return

        # If the node does not have outlinks yet
        if not links_block:
            link_node = self.__node()
            link_node.set_target(first_target_block)
            link_node.write()

            links_block = link_node.block
            source_node.set_links(link_node.block, out=out)
            source_node.write()

            first_target_block = None

        # Finding the current
        link_nodes_index = {}
        last_link_node = None

        for link_node in self.link_nodes_iter(links_block):
            link_nodes_index[link_node.target()] = link_node
            last_link_node = link_node

        if first_target_block:
            target_blocks = chain([first_target_block], target_blocks)

        # Adding new targets
        # TODO: possible to virtualize chain and flush later to ease writes
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
                last_link_node.write()
                last_link_node = link_node

    def add_outlinks(self, source_node, target_blocks):
        return self.add_links(source_node, target_blocks, out=True)

    def add_inlinks(self, source_node, target_blocks):
        return self.add_links(source_node, target_blocks, out=False)

    # =========================================================================
    # Iteration methods
    # =========================================================================
    def nodes_iter(self):
        node = self.__root()

        while node.exists:
            yield node
            node.read(node.block + self.storage.block_size)

    def link_nodes_iter(self, block):
        node = self.__node(block=block)

        if not node.exists:
            raise LinkStoreTraversalException('Block does not exist.')

        yield node

        while node.has_next():
            node.read_next()
            yield node
