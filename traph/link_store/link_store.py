# =============================================================================
# Link Store Class
# =============================================================================
#
# Class representing the structure storing the links as linked list of stubs.
# Note that linked lists are stored in reverse to allow for constant time
# addition to the list and that link weights are stored as duplication.
#
from collections import Counter
from traph.link_store.node import LinkStoreNode, LINK_STORE_FIRST_DATA_BLOCK
from traph.link_store.header import LinkStoreHeader, LINK_STORE_HEADER_BLOCKS


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
    # Read methods
    # =========================================================================

    # Method returning a node
    def node(self, **kwargs):
        return LinkStoreNode(self.storage, **kwargs)

    # Method returning the root
    def root(self):
        return self.node(block=LINK_STORE_FIRST_DATA_BLOCK)

    # =========================================================================
    # Mutation methods
    # =========================================================================
    def add_links(self, source_node, target_blocks, out=True):
        tail_node = None
        empty = True

        if source_node.has_links(out=out):
            tail_node = self.node(block=source_node.links(out=out))

        for target_block in target_blocks:
            empty = False
            link_node = self.node()
            link_node.set_target(target_block)

            if tail_node is not None:
                link_node.set_previous(tail_node.block)

            link_node.write()

            tail_node = link_node

        if not empty:
            assert tail_node is not None

            # Attaching new tail
            source_node.set_links(tail_node.block, out=out)
            source_node.write()

    def add_outlinks(self, source_node, target_blocks):
        return self.add_links(source_node, target_blocks, out=True)

    def add_inlinks(self, source_node, target_blocks):
        return self.add_links(source_node, target_blocks, out=False)

    # =========================================================================
    # Iteration methods
    # =========================================================================
    def nodes_iter(self):
        node = self.root()

        while node.exists:
            yield node
            node.read(node.block + self.storage.block_size)

    # NOTE: this method will yield blocks as is, so expect duplication!
    def link_nodes_iter(self, block):
        node = self.node(block=block)

        if not node.exists:
            raise LinkStoreTraversalException('Block does not exist.')

        yield node

        while node.has_previous():
            node.read_previous()
            yield node

    def weighted_link_nodes_iter(self, block):
        node = self.node(block=block)

        if not node.exists:
            raise LinkStoreTraversalException('Block does not exist.')

        # TODO: it's theoretically possible to rely on constant time hashing
        weights = Counter()
        weights[node.target()] = 1

        while node.has_previous():
            node.read_previous()
            weights[node.target()] += 1

        for target, weight in list(weights.items()):
            yield target, weight

    def deduped_link_nodes_iter(self, block):
        node = self.node(block=block)

        if not node.exists:
            raise LinkStoreTraversalException('Block does not exist.')

        target = node.target()

        # TODO: it's theoretically possible to rely on constant time hashing
        already_seen = set()
        already_seen.add(target)

        yield target

        while node.has_previous():
            node.read_previous()

            len_before = len(already_seen)
            target = node.target()
            already_seen.add(target)

            if len(already_seen) > len_before:
                yield target

    # =========================================================================
    # Counting methods
    # =========================================================================
    def count_links(self):
        blocks = self.storage.count_blocks() - LINK_STORE_HEADER_BLOCKS

        return blocks / 2

    def metrics(self):
        nb_links = self.count_links()

        # NOTE: we are now unable, from a LinkStore itself, to aggregate
        # meaningful values about weights. Only the Traph can do this, by
        # considering both the LinkStore and the LRUTrie.
        stats = {
            'nb_links': nb_links,
            'nb_outlinks': nb_links / 2
        }

        return stats
