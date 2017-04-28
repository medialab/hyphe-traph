# =============================================================================
# Traph Batch Class
# =============================================================================
#
# Class representing a batch of operations performed on the given traph.
#


# Main class
class TraphBatch(object):

    def __init__(self, traph):

        # Properties
        self.traph = traph
        self.links = self.traph.link_store
        self.page_cache = {}

    def add_page(self, lru):
        if lru in self.page_cache:
            return self.page_cache[lru]

        node = self.traph.add_page(lru)
        self.page_cache[lru] = node

        return node

    def add_page_with_links(self, lru, links):
        source_node = self.add_page(lru)

        generator = (self.add_page(target_lru).block for target_lru in links)
        self.links.add_links(source_node, generator)
