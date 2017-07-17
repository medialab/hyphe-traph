# =============================================================================
# Traph Class
# =============================================================================
#
# Main class representing the Traph data structure.
#
import re
from collections import defaultdict
from traph_batch import TraphBatch
from file_storage import FileStorage
from memory_storage import MemoryStorage
from lru_trie import LRUTrie
from lru_trie_walk_history import LRUTrieWalkHistory
from lru_trie_node import LRU_TRIE_NODE_BLOCK_SIZE
from link_store import LinkStore
from link_store_node import LINK_STORE_NODE_BLOCK_SIZE


# Main class
class Traph(object):

    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, create=False, folder=None,
                 default_webentity_creation_rule=None,
                 webentity_creation_rules=None):

        # TODO: solve path

        if create:
            # TODO: erase dir and all its content
            # TODO: make dir
            self.lru_trie_file = open(folder+'lru_trie.dat', 'wb+')
            self.link_store_file = open(folder+'link_store.dat', 'wb+')
        else:
            self.lru_trie_file = open(folder+'lru_trie.dat', 'rb+')
            self.link_store_file = open(folder+'link_store.dat', 'rb+')

        # LRU Trie initialization
        if folder:
            self.lru_trie_storage = FileStorage(
                LRU_TRIE_NODE_BLOCK_SIZE,
                self.lru_trie_file
            )
        else:
            self.lru_trie_storage = MemoryStorage(LRU_TRIE_NODE_BLOCK_SIZE)

        self.lru_trie = LRUTrie(self.lru_trie_storage)

        # Link Store initialization
        if folder:
            self.links_store_storage = FileStorage(
                LINK_STORE_NODE_BLOCK_SIZE,
                self.link_store_file
            )
        else:
            self.links_store_storage = MemoryStorage(
                LINK_STORE_NODE_BLOCK_SIZE)

        self.link_store = LinkStore(self.links_store_storage)

        # Web entity creation rules are stored in RAM
        self.default_webentity_creation_rule = re.compile(
            default_webentity_creation_rule,
            re.I
        )

        self.webentity_creation_rules = {}

        for prefix, pattern in webentity_creation_rules.items():
            self.add_webentity_creation_rule(prefix, pattern, create)


    # =========================================================================
    # Internal methods
    # =========================================================================
    def __add_prefixes(self, prefixes):
        for prefix in prefixes:

            # TODO: notify of webentity creation
            # TODO: 45 is a placeholder for the weid
            node, history = self.lru_trie.add_lru(prefix)
            node.set_webentity(45)
            node.write()

    def __apply_webentity_creation_rule(self, rule_prefix, lru):

        regexp = self.webentity_creation_rules[rule_prefix]
        match = regexp.search(lru)

        if not match:
            return False

        prefix = match.group()

        self.__add_prefixes(self.expand_prefix(prefix))

        return True

    def __apply_webentity_default_creation_rule(self, lru):

        regexp = self.default_webentity_creation_rule
        match = regexp.search(lru)

        if not match:
            return False

        prefix = match.group()

        self.__add_prefixes(self.expand_prefix(prefix))

        return True

    # =========================================================================
    # Public interface
    # =========================================================================
    def add_webentity_creation_rule(self, prefix, pattern, write_in_trie=True):
        print 'add webentity ' + prefix + ' - ' + str(write_in_trie)
        print self.webentity_creation_rules
        self.webentity_creation_rules[prefix] = re.compile(
            pattern,
            re.I
        )

        if write_in_trie:
            node, history = self.lru_trie.add_lru(prefix)
            node.flag_as_webentity_creation_rule()
            node.write()
        # TODO: if write_in_trie, depth first search to apply the rule (create entities)

    def expand_prefix(self, prefix):
        # TODO: expand
        return [prefix]

    def batch(self):
        return TraphBatch(self)

    def add_page(self, lru):
        node, history = self.lru_trie.add_page(lru)

        # Here we need to deal with webentity creation rules
        for rule_prefix in history.rules_to_apply():
            if self.__apply_webentity_creation_rule(rule_prefix, lru):
                return node

        self.__apply_webentity_default_creation_rule(lru)
        return node

    def add_links(self, links):
        store = self.link_store

        # TODO: this will need to return created web entities
        inlinks = defaultdict(list)
        outlinks = defaultdict(list)
        pages = dict()

        for source_page, target_page in links:

            # Adding pages
            if not source_page in pages:
                node = self.add_page(source_page)
                pages[source_page] = node
            if not target_page in pages:
                node = self.add_page(target_page)
                pages[target_page] = node

            # Handling multimaps
            outlinks[source_page].append(target_page)
            inlinks[target_page].append(source_page)

        for source_page, target_pages in outlinks.items():
            source_node = pages[source_page]
            target_blocks = (pages[target_page].block for target_page in target_pages)

            store.add_outlinks(source_node, target_blocks)

        for target_page, source_pages in inlinks.items():
            target_node = pages[target_page]
            source_blocks = (pages[source_page].block for source_page in source_pages)

            store.add_inlinks(target_node, source_blocks)

    def close(self):

        # Cleanup
        self.lru_trie_file.close()
        self.link_store_file.close()

    # =========================================================================
    # Iteration methods
    # =========================================================================
    def links_iter(self, out=True):
        for page_node, lru in self.lru_trie.pages_iter():
            for target_block in self.link_store.link_nodes_iter(page_node.outlinks()):
                yield lru, target_block
